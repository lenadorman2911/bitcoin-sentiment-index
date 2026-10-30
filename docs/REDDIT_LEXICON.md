# Archived cryptocurrency lexicon additions

These 36 entries and valence values are transcribed programmatically from `collectors/crypto_lexicon.py`. That Python dictionary remains authoritative. They are added to the VADER lexicon by `collectors/legacy_reddit_definition.py`; the per-post measure is VADER compound, not the arithmetic mean of these word values.

The archived definition combines post title and body and takes the unweighted mean of post compound scores for each day. Failed retrievals and days without scored posts remain missing. The source includes multiword dictionary keys; listing them does not establish that VADER matches every phrase as intended. No phrase-matching or human-validation claim is made by this documentation.

The legacy collector uses naive datetime timestamp boundaries and timestamp-based pagination. It documents the archived procedure, not a guarantee of complete UTC-day coverage or exact regeneration of the frozen aggregate. See `collectors/README.md`.

| Entry | Valence |
| --- | ---: |
| moon | +2.5 |
| mooning | +2.7 |
| to the moon | +3 |
| bullish | +2.5 |
| hodl | +1.5 |
| ath | +2 |
| pump | +1.8 |
| pumping | +2 |
| lambo | +2.2 |
| diamond hands | +2 |
| buy the dip | +1.5 |
| wagmi | +2.3 |
| degen | +0.5 |
| green candle | +1.8 |
| rekt | -2.8 |
| rug pull | -3.2 |
| rugged | -3 |
| bearish | -2.5 |
| dump | -2 |
| dumping | -2.2 |
| crash | -2.9 |
| capitulation | -2.7 |
| paper hands | -1.5 |
| ngmi | -2.3 |
| red candle | -1.8 |
| liquidated | -2.9 |
| liquidation | -2.5 |
| fud | -1.8 |
| bagholder | -2 |
| insolvent | -3.3 |
| insolvency | -3.3 |
| contagion | -2.6 |
| exploit | -2.4 |
| hacked | -2.9 |
| depeg | -2.8 |
| depegged | -2.8 |
