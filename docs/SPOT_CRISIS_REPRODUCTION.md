# Spot volume crisis reproduction

This extension reproduces the six primary component-weighted crisis readings reported in the revised article. It compares the reduced market and behavioral index with its volume-excluded and spot taker-buy replacement variants. All three use Sample A calibration, from 1 November 2021 to 26 August 2026, and a 90-observation normalization window.

| Construction | LUNA 11 May 2022 | FTX 8 November 2022 |
| --- | ---: | ---: |
| Original unsigned volume | 65.55 | 87.92 |
| Exclude unsigned volume | 1.16 | 23.56 |
| Replace with spot taker-buy quote-volume share | 1.04 | 22.35 |

The scores are retrospective. Weights are re-estimated for each construction. Each score ranks that construction against its own expanding history through the observation date. These comparisons do not isolate the effect of direction while holding weights fixed, or establish a forecasting advantage. The original baseline futures taker-buy component and the new spot series remain separate.

## Inputs and installation

Run commands from the repository root. Python 3.11 or later, NumPy and pandas are required. The package was checked using the versions recorded in `reproduction/spot_crisis/reference/package_validation.json`.

```sh
python -m pip install -r reproduction/spot_crisis/requirements.txt
python -m unittest discover -s reproduction/spot_crisis -p test_reproduction.py -v
```

Exact reproduction requires an authorized copy of the existing frozen prepared input. Its SHA-256 is `0a07ba4e54987a3d44c086adcb1fe019d6743c3378a28a5cf43f7945a526b9cc`. It contains 3,297 daily rows from 17 August 2017 to 26 August 2026. Place it at `data/private/analysis_input.csv` or pass its actual location with `--input`. This extension does not distribute that combined input.

The calculation reads `log_return` and the nine original reduced-index `_rz_90` component columns. Their existing normalization and frozen Google/Reddit definitions are retained. The replacement share is calculated from spot quote volumes and normalized using a rolling mean and sample standard deviation with 90 valid daily observations. Missing components retain the original daily weight-renormalization rule.

## Prepare the spot observations

The pinned manifest lists the 109 monthly Binance BTCUSDT spot daily-kline archives used in the original collection on 25 October 2026. Every archive must match both its provider CHECKSUM and its archived SHA-256. Timestamps are milliseconds before January 2025 and microseconds thereafter. Daily observations use UTC dates.

For archives already downloaded to a local directory:

```sh
python reproduction/spot_crisis/collect.py --archive-dir data/private/binance-spot-archives --output data/private/spot-crisis-collection
```

To permit downloads of missing archives, add `--fetch`. Review the provider's data terms before downloading:

```sh
python reproduction/spot_crisis/collect.py --archive-dir data/private/binance-spot-archives --output data/private/spot-crisis-collection --fetch
```

The output contains `spot_daily.csv` and `collection_verification.json`. The share equals taker-buy quote volume divided by total quote volume, both in USDT. Zero total volume produces a missing share. A changed archive hash stops the run rather than silently substituting a newer vintage. Raw Binance archives and the combined input are absent from this update archive.

## Reproduce the article values

```sh
python reproduction/spot_crisis/reproduce.py --input data/private/analysis_input.csv --spot-input data/private/spot-crisis-collection/spot_daily.csv --output results/spot-crisis-check
```

An existing original combined spot/futures CSV can also be supplied through `--spot-input`. The script selects only records labeled `spot`.

The output directory must be new. A successful run writes:

- `crisis_readings.csv`: six full-precision scores and unranked values.
- `component_weights.csv`: 26 weights, stress correlations, valid-pair counts and thresholds across the three constructions.
- `verification.json`: input hashes, software versions and numerical comparison errors.

The script checks all six scores and all 26 component weights against the archived 25 October calculations. The original prepared-input hash is mandatory. Reproduction of these archived results is distinct from validation of sentiment meaning or a new out-of-sample test.

## Source and validation records

`reference/input_manifest.json` identifies the required prepared input and the original spot/futures collection. `reference/spot_archive_manifest.csv` identifies the spot downloads. The crisis and weight references are selected from the existing archived calculation, not newly estimated targets. `reference/package_validation.json` records the local checks of this portable implementation.

The statistical suite, allocation tests, and complete Exhibit 4 EW/full-index results use the existing repository workflow. This focused extension reproduces the six reduced CW values above. See [the result map](MANUSCRIPT_RESULTS_MAP.md) for the distinction.

Code follows the repository's MIT license. Source datasets retain their own terms. See [data publication notes](DATA_PUBLICATION_NOTES.md).
