# Bitcoin spot taker-buy volume

This frozen dataset contains 3,297 daily Binance BTCUSDT spot observations from 17 August 2017 through 26 August 2026. It supplies the historical spot-volume input for the LUNA/FTX replacement diagnostic in the Bitcoin sentiment study.

Source: Binance Vision / Binance Public Data, BTCUSDT spot monthly daily-kline archives, https://data.binance.vision/ and https://github.com/binance/binance-public-data.

Data license: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0), https://creativecommons.org/licenses/by-nc-sa/4.0/. See [LICENSE.md](LICENSE.md) for the source terms and attribution notice. The repository's code license does not replace this dataset license. Binance does not endorse this study.

## Files and definitions

`btc_spot_taker_buy_daily_2017_2026.csv` is a plain UTF-8 CSV with one header row. Dates are UTC calendar dates. Decimal points use periods. The share is stored as a fraction, not percentage points. All four columns are complete in this frozen snapshot.

| Column | Definition | Unit |
| --- | --- | --- |
| `date` | UTC date of the daily BTCUSDT spot kline | ISO date, YYYY-MM-DD |
| `volume_usdt` | Total quote-asset volume in the daily spot kline | USDT |
| `taker_buy_usdt` | Taker-buy quote-asset volume in the same daily spot kline | USDT |
| `buy_share_quote` | `taker_buy_usdt / volume_usdt` | Fraction from 0 to 1 |

`source_archive_manifest.csv` records the 109 monthly archive URLs, original SHA-256 hashes, row counts and timestamp units. `provenance.json` records source and preparation details. `validation.json` records checks of dates, volume identities and the previously reported crisis calculation. `verify.py` checks this public CSV without a private input or third-party Python packages.

## Preparation and attribution

The original archives were downloaded on 25 October 2026. This release was prepared on 8 November 2026 from those saved, checksum-verified archives. It preserves that download vintage rather than querying current values.

Changes from the source archives: select the total and taker-buy quote-volume fields, convert daily open times to UTC dates, combine monthly files, restrict observations to the study end date, and calculate the taker-buy share. Timestamp parsing accounts for the change from milliseconds to microseconds in January 2025. No missing dates or values were interpolated.

Suggested attribution: “Source: Binance Vision, BTCUSDT spot daily klines, archived 25 October 2026. Quote-volume fields selected and taker-buy share calculated by Elena Dorman.” Retain the source link, license link, and this description of changes when redistributing an adapted dataset.

## Verify and reproduce

From the repository root:

```sh
python data/public/binance_spot/verify.py
```

The file is directly compatible with the previously published spot-crisis script:

```sh
python reproduction/spot_crisis/reproduce.py --input data/private/analysis_input.csv --spot-input data/public/binance_spot/btc_spot_taker_buy_daily_2017_2026.csv --output results/spot-crisis-public-data
```

That index calculation also needs the authorized prepared input containing the other sentiment components. This public file supplies the spot-volume component only. Taker-buy share measures aggressor-side buying, which does not directly observe investor beliefs.
