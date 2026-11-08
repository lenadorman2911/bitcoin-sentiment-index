"""Small tests of the assumptions that affect crisis-score interpretation."""
import io
import hashlib
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

import numpy as np
import pandas as pd

from collect import parse_archive, obtain
from reproduce import aggregate, fit_weights


class CrisisTests(unittest.TestCase):
    def test_changed_archive_is_rejected_against_pinned_hash(self):
        expected = b'original archive'
        record = {'url': 'https://data.binance.vision/data/spot/monthly/test.zip',
                  'sha256': hashlib.sha256(expected).hexdigest()}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'test.zip').write_bytes(b'changed archive')
            (root/'test.zip.CHECKSUM').write_text(record['sha256'] + '  test.zip\n')
            with self.assertRaises(ValueError):
                obtain(record, root, False)

    def test_unavailable_components_renormalize_weights(self):
        x = pd.DataFrame({'a': [2., np.nan, np.nan], 'b': [4., 4., np.nan]})
        weights = pd.DataFrame({'component': ['a', 'b'], 'weight': [.25, .75]})
        actual = aggregate(x, {'a': 1, 'b': -1}, weights)
        np.testing.assert_allclose(actual.iloc[:2], [-2.5, -4.])
        self.assertTrue(np.isnan(actual.iloc[2]))

    def test_outcomes_after_calibration_end_do_not_change_weights(self):
        dates = pd.Series(pd.date_range('2021-11-01', '2026-08-28'))
        n = len(dates)
        returns = pd.Series(np.sin(np.arange(n)*.17)*.06)
        features = pd.DataFrame({'a': np.sin(np.arange(n)*.11), 'b': np.cos(np.arange(n)*.13)})
        expected = fit_weights(features, returns, dates)
        changed = returns.copy()
        changed.loc[dates.gt('2026-08-26')] = 1000.
        actual = fit_weights(features, changed, dates)
        pd.testing.assert_frame_equal(actual, expected)

    def test_spot_timestamp_units_and_quote_fields(self):
        for date, unit in [('2022-05-11', 'ms'), ('2025-01-01', 'us')]:
            timestamp = pd.Timestamp(date, tz='UTC').value // (10**6 if unit == 'ms' else 10**3)
            row = [timestamp, 1, 1, 1, 1, 10, timestamp, 100, 2, 4, 35, 0]
            buffer = io.BytesIO()
            with ZipFile(buffer, 'w') as archive:
                archive.writestr('klines.csv', ','.join(map(str, row)) + '\n')
            frame, detected = parse_archive(buffer.getvalue())
            self.assertEqual(detected, unit)
            self.assertEqual(frame.date.iloc[0], pd.Timestamp(date))
            self.assertEqual(frame.volume_usdt.iloc[0], 100)
            self.assertEqual(frame.taker_buy_usdt.iloc[0], 35)


if __name__ == '__main__':
    unittest.main()
