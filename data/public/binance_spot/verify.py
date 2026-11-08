"""Check the public spot-volume CSV using only the Python standard library."""
import csv
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root/'provenance.json').read_text())
    path = root/manifest['file']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest['sha256']:
        raise ValueError('CSV SHA-256 differs from the published frozen snapshot')
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['date','volume_usdt','taker_buy_usdt','buy_share_quote']:
            raise ValueError('Unexpected CSV schema')
        rows = list(reader)
    expected_date = date(2017,8,17)
    max_error = 0.
    for row in rows:
        observed = date.fromisoformat(row['date'])
        if observed != expected_date:
            raise ValueError('Missing, duplicate or unsorted date: '+row['date'])
        expected_date += timedelta(days=1)
        total, buy, share = [float(row[x]) for x in ['volume_usdt','taker_buy_usdt','buy_share_quote']]
        if not all(math.isfinite(v) for v in [total,buy,share]):
            raise ValueError('Missing or non-finite value: '+row['date'])
        if not (total > 0 and 0 <= buy <= total and 0 <= share <= 1):
            raise ValueError('Invalid quote-volume observation: '+row['date'])
        error=abs(share-buy/total)
        if error > 1e-14:
            raise ValueError('Taker-buy share does not match quote volumes: '+row['date'])
        max_error=max(max_error,error)
    if len(rows)!=3297 or expected_date!=date(2026,8,27):
        raise ValueError('Unexpected date coverage')
    print(json.dumps({'status':'passed','rows':len(rows),'start':rows[0]['date'],
                      'end':rows[-1]['date'],'sha256':digest,
                      'maximum_share_absolute_error':max_error},indent=2))


if __name__=='__main__':
    main()
