"""Reproduce the six primary retrospective CW crisis scores in the manuscript."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
START, END, WINDOW = '2021-11-01', '2026-08-26', 90
EVENTS = {'LUNA': '2022-05-11', 'FTX': '2022-11-08'}
DIRECTIONS = {
    'momentum_7d': 1,
    'volatility_30d': -1,
    'btc_dominance_proxy': -1,
    'volume_usd_proxy': 1,
    'usdt_dominance': -1,
    'google_trends_sentiment_ratio': 1,
    'wikipedia_views_bitcoin': 1,
    'reddit_sentiment_score': 1,
    'github_commits': 1,
}


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def validate_dates(frame, label):
    if frame.date.isna().any() or frame.date.duplicated().any():
        raise ValueError(f'{label}: dates must be present and unique')
    if not frame.date.is_monotonic_increasing:
        raise ValueError(f'{label}: dates must be sorted in ascending order')
    if not frame.date.eq(frame.date.dt.normalize()).all():
        raise ValueError(f'{label}: use UTC calendar dates without intraday times')


def fit_weights(features, log_returns, dates):
    mask = dates.between(START, END)
    x = features.loc[mask].reset_index(drop=True)
    # Shift only within the calibration sample: the final date has no outcome.
    future = log_returns.loc[mask].reset_index(drop=True).abs().shift(-1)
    threshold = float(future.quantile(0.90))
    stress = future.ge(threshold)
    rows = []
    for name in x:
        valid = stress & x[name].notna() & future.notna()
        count = int(valid.sum())
        if count < 30:
            raise ValueError(f'{name}: fewer than 30 valid stress observations')
        a, b = x.loc[valid, name].rank(), future.loc[valid].rank()
        rho = float(np.corrcoef(a.to_numpy(), b.to_numpy())[0, 1])
        if not np.isfinite(rho):
            raise ValueError(f'{name}: undefined stress correlation')
        rows.append({'component': name, 'stress_pairs': count,
                     'rho': rho, 'raw_weight': abs(rho), 'q90': threshold})
    weights = pd.DataFrame(rows)
    total = weights.raw_weight.sum()
    if total <= 0:
        raise ValueError('CW calibration produced no positive total weight')
    weights['weight'] = weights.raw_weight / total
    return weights


def aggregate(features, directions, weights):
    w = weights.set_index('component').weight.reindex(features.columns)
    signed = features.mul(pd.Series(directions).reindex(features.columns))
    denominator = features.notna().mul(w).sum(axis=1).replace(0, np.nan)
    return signed.mul(w).sum(axis=1) / denominator


def calculate(data, spot):
    required = ['log_return'] + [name + '_rz_90' for name in DIRECTIONS]
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError('Missing prepared-input columns: ' + ', '.join(missing))
    validate_dates(data, 'Prepared input')
    if 'market' in spot:
        spot = spot.loc[spot.market.eq('spot')].copy()
    spot = spot.sort_values('date').reset_index(drop=True)
    validate_dates(spot, 'Spot data')
    volume_columns = ['volume_usdt', 'taker_buy_usdt']
    if not set(volume_columns).issubset(spot):
        raise ValueError('Spot CSV requires volume_usdt and taker_buy_usdt')
    values = spot[volume_columns].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError('Spot volumes must be finite and nonnegative')
    if (spot.taker_buy_usdt > spot.volume_usdt + 1e-4).any():
        raise ValueError('Taker-buy quote volume exceeds total quote volume')
    expected_dates = pd.date_range(data.date.min(), END)
    if not data.date.equals(pd.Series(expected_dates, name='date')):
        raise ValueError('Prepared input must have uninterrupted daily history through the end date')
    if not pd.Index(expected_dates).isin(spot.date).all():
        raise ValueError('Spot history does not cover all prepared-input dates')
    share = spot.set_index('date').taker_buy_usdt / spot.set_index('date').volume_usdt.replace(0, np.nan)
    aligned = data.date.map(share)
    rolling = aligned.rolling(WINDOW, min_periods=WINDOW)
    z = (aligned - rolling.mean()) / rolling.std(ddof=1).replace(0, np.nan)
    base = pd.DataFrame({name: data[name + '_rz_90'] for name in DIRECTIONS})
    readings, parameter_rows = [], []
    for variant in ['original_volume', 'without_volume', 'spot_buy_share_quote']:
        x, directions = base.copy(), DIRECTIONS.copy()
        if variant != 'original_volume':
            x = x.drop(columns='volume_usd_proxy')
            directions.pop('volume_usd_proxy')
        if variant == 'spot_buy_share_quote':
            x['spot_buy_share_quote'] = z
            directions['spot_buy_share_quote'] = 1
        weights = fit_weights(x, data.log_return, data.date)
        weights.insert(0, 'variant', variant)
        parameter_rows.append(weights)
        raw = aggregate(x, directions, weights)
        scores = raw.expanding().rank(pct=True) * 100
        for event, date in EVENTS.items():
            positions = data.index[data.date.eq(date)]
            if len(positions) != 1:
                raise ValueError('Missing crisis date: ' + date)
            i = positions[0]
            readings.append({'variant': variant, 'event': event, 'date': date,
                             'score': float(scores.loc[i]), 'raw_index': float(raw.loc[i])})
    return pd.DataFrame(readings), pd.concat(parameter_rows, ignore_index=True)


def verify(readings, weights):
    keys = ['variant', 'event', 'date']
    expected = pd.read_csv(HERE/'reference/crisis_readings.csv')
    actual = readings.merge(expected, on=keys, validate='one_to_one', suffixes=('', '_expected'))
    if len(actual) != 6 or len(readings) != 6:
        raise ValueError('Expected exactly six primary crisis results')
    errors = {}
    for name in ['score', 'raw_index']:
        np.testing.assert_allclose(actual[name], actual[name + '_expected'], atol=1e-10, rtol=1e-10)
        errors[name] = float(np.max(np.abs(actual[name] - actual[name + '_expected'])))
    reference_weights = pd.read_csv(HERE/'reference/component_weights.csv')
    compared = weights.merge(reference_weights, on=['variant', 'component'],
                             validate='one_to_one', suffixes=('', '_expected'))
    if len(compared) != 26 or len(weights) != 26:
        raise ValueError('Expected 26 component-weight records')
    for name in ['weight', 'rho', 'q90', 'stress_pairs']:
        np.testing.assert_allclose(compared[name], compared[name + '_expected'], atol=1e-10, rtol=1e-10)
    errors['weight'] = float(np.max(np.abs(compared.weight - compared.weight_expected)))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Authorized frozen analysis_input.csv')
    parser.add_argument('--spot-input', type=Path, required=True, help='Spot-only CSV or original spot/futures archive CSV')
    parser.add_argument('--output', type=Path, required=True, help='New directory for results')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output directory: ' + str(args.output))
    manifest = json.loads((HERE/'reference/input_manifest.json').read_text())
    input_hash, spot_hash = sha256(args.input), sha256(args.spot_input)
    if input_hash != manifest['prepared_input']['sha256']:
        raise ValueError('Prepared input SHA-256 differs from the archived manuscript input')
    data = pd.read_csv(args.input, parse_dates=['date'])
    spot = pd.read_csv(args.spot_input, parse_dates=['date'])
    if len(data) != manifest['prepared_input']['rows']:
        raise ValueError('Unexpected number of prepared-input dates')
    readings, weights = calculate(data, spot)
    errors = verify(readings, weights)
    if sha256(args.input) != input_hash or sha256(args.spot_input) != spot_hash:
        raise RuntimeError('An input changed during calculation')
    report = {'status': 'passed', 'crisis_results_checked': 6, 'component_weights_checked': 26,
              'prepared_input_sha256': input_hash, 'spot_input_sha256': spot_hash,
              'maximum_absolute_errors': errors, 'python': platform.python_version(),
              'numpy': np.__version__, 'pandas': pd.__version__,
              'scope': 'Sample A, reduced market-and-behavioral CW, W=90, retrospective',
              'interpretation': 'Weights are refitted for each variant and each percentile uses its own expanding history.'}
    args.output.mkdir(parents=True, exist_ok=False)
    readings.to_csv(args.output/'crisis_readings.csv', index=False)
    weights.to_csv(args.output/'component_weights.csv', index=False)
    (args.output/'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(readings[['variant', 'event', 'score']].to_string(index=False))
    print('PASS: six archived readings and 26 weights matched. Results: ' + str(args.output))


if __name__ == '__main__':
    main()
