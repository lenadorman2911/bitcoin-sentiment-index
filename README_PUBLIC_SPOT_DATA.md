# Public spot-volume data addition

The frozen daily [Binance spot-volume dataset](data/public/binance_spot/README.md) now supplies the spot component used in the historical LUNA/FTX diagnostic. It contains 3,297 UTC daily records from 17 August 2017 to 26 August 2026, with total quote volume, taker-buy quote volume and their ratio.

The dataset is derived from the 109 monthly Binance archives identified in its source manifest. Its source-specific license is CC BY-NC-SA 4.0, with source attribution and changes documented beside the CSV. It is separate from the MIT license on project code.

The existing `reproduction/spot_crisis/reproduce.py` accepts this public CSV through `--spot-input`. The complete prepared input for the remaining index components is still required for exact reproduction of the index results.

After uploading this addition, link the dataset README from the main README and `docs/SPOT_CRISIS_REPRODUCTION.md`. The CSV provides a direct alternative to the archive-download step described there. Existing software and data releases remain historical records until a new release is created.
