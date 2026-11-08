"""Verify cached Binance spot archives, optionally downloading missing files."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_archive(payload):
    with ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if len(names) != 1:
            raise ValueError('A monthly kline archive must contain exactly one CSV')
        frame = pd.read_csv(io.BytesIO(archive.read(names[0])), header=None)
    frame = frame.loc[pd.to_numeric(frame[0], errors='coerce').notna()].copy()
    frame = frame.apply(pd.to_numeric, errors='raise')
    if frame.shape[1] != 12:
        raise ValueError('Unexpected Binance kline schema')
    unit = 'us' if frame[0].median() > 1e14 else 'ms'
    dates = pd.to_datetime(frame[0], unit=unit, utc=True).dt.tz_localize(None)
    if not dates.eq(dates.dt.normalize()).all():
        raise ValueError('Klines are not aligned to UTC daily boundaries')
    output = pd.DataFrame({'date': dates, 'volume_usdt': frame[7], 'taker_buy_usdt': frame[10]})
    values = output[['volume_usdt', 'taker_buy_usdt']].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError('Invalid volume observation')
    if (output.taker_buy_usdt > output.volume_usdt + 1e-4).any():
        raise ValueError('Taker-buy volume exceeds total volume')
    return output, unit


def obtain(record, archive_dir, fetch):
    target = archive_dir/Path(record['url']).name
    checksum = target.with_suffix(target.suffix + '.CHECKSUM')
    if not target.exists() or not checksum.exists():
        if not fetch:
            raise FileNotFoundError(f'Archive or checksum missing: {target}. Download manually or use --fetch.')
        # Fetch both bytes before writing. Pin identity to the original archive manifest.
        with urlopen(record['url'], timeout=60) as response:
            payload = response.read()
        with urlopen(record['url'] + '.CHECKSUM', timeout=60) as response:
            check = response.read()
        if digest(payload) != record['sha256'] or check.decode().split()[0] != record['sha256']:
            raise ValueError('Downloaded archive differs from the archived provider checksum: ' + record['url'])
        archive_dir.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != payload:
            raise FileExistsError('Refusing to replace a different cached archive: ' + str(target))
        if checksum.exists() and checksum.read_bytes() != check:
            raise FileExistsError('Refusing to replace a different cached checksum: ' + str(checksum))
        if not target.exists():
            target.write_bytes(payload)
        if not checksum.exists():
            checksum.write_bytes(check)
    payload = target.read_bytes()
    if digest(payload) != record['sha256'] or checksum.read_text().split()[0] != record['sha256']:
        raise ValueError('Cached archive/checksum differs from the pinned manifest: ' + str(target))
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New directory for the spot CSV and verification')
    parser.add_argument('--fetch', action='store_true', help='Download missing files from Binance; otherwise offline only')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output directory: ' + str(args.output))
    manifest = pd.read_csv(HERE/'reference/spot_archive_manifest.csv')
    frames, units = [], set()
    for record in manifest.to_dict('records'):
        frame, unit = parse_archive(obtain(record, args.archive_dir, args.fetch))
        frames.append(frame)
        units.add(unit)
    data = pd.concat(frames).query('date <= "2026-08-26"').sort_values('date').reset_index(drop=True)
    expected = pd.Series(pd.date_range('2017-08-17', '2026-08-26'), name='date')
    if not data.date.equals(expected):
        raise ValueError('Spot dates contain gaps, duplicates or an unexpected range')
    data['buy_share_quote'] = data.taker_buy_usdt/data.volume_usdt.replace(0, np.nan)
    args.output.mkdir(parents=True, exist_ok=False)
    data.to_csv(args.output/'spot_daily.csv', index=False)
    result = {'status': 'passed', 'archives_checked': len(manifest), 'rows': len(data),
              'start': '2017-08-17', 'end': '2026-08-26', 'timestamp_units_seen': sorted(units),
              'all_archive_hashes_match_2026_10_25_manifest': True,
              'spot_csv_sha256': digest((args.output/'spot_daily.csv').read_bytes()),
              'network_enabled': args.fetch, 'source': 'Binance Public Data BTCUSDT spot daily klines'}
    (args.output/'collection_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
