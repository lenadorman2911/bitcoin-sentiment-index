# Optional collection definitions

These files are separate from offline numerical reproduction. None is run by `run_analysis.py`.

`google_common_anchor.py` documents the six-query common-anchor ratio. Install `requirements-collection.txt` to use it. For example, from the repository directory:

```bash
python collectors/google_common_anchor.py --start 2021-08-04 --end 2026-08-26 --out data/private/new-google --cache data/private/google-cache --fetch --max-requests 24
```

The command makes live network requests only with explicit `--fetch`. It creates a new retrieval vintage and cannot be assumed to reproduce the frozen data. Request limits or provider changes may stop it. The 24-request budget covers the original twelve paired windows only if uncached requests succeed. Cached requests must use matching metadata and dependency versions.

`legacy_reddit_definition.py` and `crypto_lexicon.py` document the archived scoring definition. They do not contain raw posts or silently recollect Reddit. The legacy implementation used naive datetime timestamp boundaries and timestamp-based pagination; archive coverage and time-zone assumptions are limitations, not guarantees of complete UTC-day reconstruction. Recollecting today does not reproduce the frozen aggregate.

`feature_definitions.py` records market-derived feature formulas. It is not a complete API collection/merge pipeline. The remaining collectors, historical GitHub export and raw-source archives require separate preparation before end-to-end reproduction from raw downloads can be claimed.
