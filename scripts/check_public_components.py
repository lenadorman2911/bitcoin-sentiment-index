import argparse
import csv
import hashlib
import json
import math
import statistics
from datetime import date, timedelta
from pathlib import Path


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def validate(root, verify_manifest=True):
    folder = root / 'data/public'
    files = [('wikipedia_pageviews.csv', 'wikipedia_views_bitcoin', 3297),
             ('google_trends_component.csv', 'google_trends_sentiment_ratio', 1849),
             ('alternative_me_cfgi.csv', 'cfgi', 3126)]
    series = {}
    coverage = {}
    for filename, field, expected in files:
        rows = read_csv(folder / filename)
        dates = [row['date'] for row in rows]
        require(len(rows) == expected and len(set(dates)) == expected, 'Row count or duplicate dates: ' + filename)
        start = date.fromisoformat(dates[0])
        require(dates == sorted(dates), 'Unsorted dates: ' + filename)
        stop = date.fromisoformat(dates[-1])
        calendar = {(start + timedelta(days=i)).isoformat() for i in range((stop-start).days+1)}
        missing_dates = sorted(calendar - set(dates))
        expected_missing = ['2018-04-14', '2018-04-15', '2018-04-16'] if field == 'cfgi' else []
        require(missing_dates == expected_missing, 'Unexpected missing dates: ' + filename)
        values = [float(row[field]) for row in rows]
        require(all(math.isfinite(v) for v in values), 'Missing/non-finite values: ' + filename)
        if field == 'google_trends_sentiment_ratio':
            require(all(-1 <= v <= 1 for v in values), 'Google ratio range')
        elif field == 'cfgi':
            require(all(0 <= v <= 100 and v.is_integer() for v in values), 'CFGI range')
        else:
            require(all(v >= 0 and v.is_integer() for v in values), 'Pageview range')
        series[field] = dict(zip(dates, values))
        coverage[filename] = dict(rows=len(rows), start=dates[0], end=dates[-1], missing_dates=missing_dates)
    metadata = json.loads((folder / 'google_requests.json').read_text())
    require(len(metadata) == 24, 'Expected 24 archived Google requests')
    grouped = {item['request_id']: {} for item in metadata}
    require(len(grouped) == len(metadata), 'Duplicate request IDs')
    query_rows = read_csv(folder / 'google_query_values.csv')
    for row in query_rows:
        require(row['request_id'] in grouped, 'Unknown Google request')
        value = float(row['interest'])
        require(math.isfinite(value) and 0 <= value <= 100, 'Invalid query value')
        value = int(value) if value.is_integer() else value
        require(row['is_partial'] in ('true', 'false'), 'Invalid partial flag')
        day = grouped[row['request_id']].setdefault(row['date'], {'date': row['date'], 'isPartial': row['is_partial'] == 'true'})
        require(day['isPartial'] == (row['is_partial'] == 'true'), 'Inconsistent partial flags')
        require(row['query'] not in day, 'Duplicate query row')
        day[row['query']] = value
    reconstructed = {}
    for i in range(0, len(metadata), 2):
        gmeta, fmeta = metadata[i:i+2]
        for item in (gmeta, fmeta):
            payload = [grouped[item['request_id']][day] for day in sorted(grouped[item['request_id']])]
            require(all(set(row) == {'date', 'isPartial', *item['spec']['queries']} for row in payload), 'Query columns differ')
            require(digest(payload) == item['payload_hash'], 'Archived Google response fingerprint differs')
        require(gmeta['spec']['start'] == fmeta['spec']['start'] and gmeta['spec']['end'] == fmeta['spec']['end'], 'Unpaired Google windows')
        greed = grouped[gmeta['request_id']]
        fear = grouped[fmeta['request_id']]
        for day in sorted(set(greed) | set(fear)):
            if day in reconstructed:
                continue
            value = None
            if day in greed and day in fear:
                g, f = greed[day], fear[day]
                ag, af = g['buy bitcoin'], f['buy bitcoin']
                if not g['isPartial'] and not f['isPartial'] and ag > 0 and af > 0:
                    gv = sum(g[q] for q in ('buy bitcoin', 'bitcoin price prediction', 'bitcoin ath')) / 3 / ag
                    fv = sum(f[q] for q in ('sell bitcoin', 'bitcoin crash', 'is bitcoin dead')) / 3 / af
                    if gv + fv > 0:
                        value = (gv - fv) / (gv + fv)
            reconstructed[day] = value
    expected = series['google_trends_sentiment_ratio']
    require(set(reconstructed) == set(expected), 'Google ratio dates differ')
    require(all(reconstructed[day] is not None for day in expected), 'Unusable Google observations')
    maximum_ratio_error = max(abs(reconstructed[day] - expected[day]) for day in expected)
    require(maximum_ratio_error <= 1e-12, 'Google ratio reconstruction differs')
    reference = read_csv(folder / 'rolling_z_reference.csv')
    require(len(reference) == 3297, 'Normalization calendar size')
    require([r['date'] for r in reference] == list(series['wikipedia_views_bitcoin']), 'Normalization calendar differs')
    maximum_z_error = 0.0
    checked = 0
    for field in ('wikipedia_views_bitcoin', 'google_trends_sentiment_ratio'):
        values = [series[field].get(row['date']) for row in reference]
        for i, row in enumerate(reference):
            for window in (7, 30, 60, 90):
                value = None
                sample = values[max(0, i-window+1):i+1]
                if len(sample) == window and all(v is not None for v in sample):
                    sd = statistics.stdev(sample)
                    if sd > 0:
                        value = (sample[-1] - statistics.mean(sample)) / sd
                saved = row[f'{field}_rz_{window}']
                require((value is None) == (saved == ''), 'Normalization missing-value mismatch')
                if value is not None:
                    error = abs(value - float(saved))
                    require(math.isfinite(error) and error <= 1e-8, 'Normalization value mismatch')
                    maximum_z_error = max(maximum_z_error, error)
                    checked += 1
    if verify_manifest:
        manifest = json.loads((folder / 'manifest.json').read_text())
        for relative, expected_hash in manifest['files'].items():
            path = (root / relative).resolve()
            require(root.resolve() in path.parents, 'Unsafe manifest path')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash, 'File fingerprint differs: ' + relative)
    return dict(status='passed', coverage=coverage, archived_google_requests=len(metadata),
                raw_google_query_rows=len(query_rows), google_ratio_max_abs_difference=maximum_ratio_error,
                normalization_values_checked=checked, normalization_max_abs_difference=maximum_z_error,
                normalization_absolute_tolerance=1e-8, scope='Three components only, not full manuscript replication')


def main():
    parser = argparse.ArgumentParser(description='Verify frozen public study components offline without writing files.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(validate(args.root.resolve()), indent=2))


if __name__ == '__main__':
    main()
