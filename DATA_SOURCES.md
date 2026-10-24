# Data provenance and distribution

The frozen analysis input contains derived daily features. The repository records its content hash but does not publish it. Provider access, availability and redistribution rights are separate issues. No claim is made that all historical values remain retrievable today.

| Component or reference | Source and meaning | Main limitation |
| --- | --- | --- |
| Momentum, realized volatility, trading-volume measures | Binance market observations; transformed into daily features | Exchange-specific coverage; activity does not identify sentiment direction |
| BTC-to-ETH price ratio | Relative prices | Not Bitcoin market-capitalization dominance |
| Funding-rate z-score | Binance futures funding | Positioning proxy, not direct sentiment |
| Liquidation-intensity proxy | Absolute daily return multiplied by Bitcoin-denominated volume | Not actual observed liquidations |
| Futures taker-buy share | Binance futures data retained for later sample | Distinct from spot volume; do not backfill earlier sample silently |
| DVOL | Deribit Bitcoin implied-volatility series | Options-implied risk measure |
| USDT share of stablecoin capitalization | DeFiLlama stablecoin capitalization | Not USDT share of the entire crypto market |
| Google greed–fear ratio | Six individual queries; common anchor in both requests | Retrieval vintage, rounding, sparse terms and unvalidated emotional labels |
| Wikipedia Bitcoin pageviews | Wikipedia pageview observations | Attention, not optimism or pessimism |
| Reddit sentiment | Frozen r/Bitcoin archive aggregates; VADER with project lexicon | Legacy collection/scoring limitations; not a newly corrected Reddit series |
| Bitcoin Core commits | Historical export and GitHub API observations | Development activity, uncertain sentiment direction |
| CFGI | Alternative.me published index | External benchmark, not observed true sentiment |
| VIX | Archived US equity implied-volatility reference | Calendar gaps; not crypto-specific sentiment |

## Frozen input schema

Required baseline fields are `date`, `price`, `return`, `log_return`, `cfgi`, `vix`, and rolling-normalized columns for each component in `scripts/build_cw_index_versions.py`. A normalized column is named `<component>_rz_<window>`, with windows 7, 30, 60 and 90. The calculation uses a daily rolling mean and sample standard deviation; insufficient or zero-variance windows remain missing. Do not fill component gaps with zero.

The complete schema is listed in `data/data_dictionary.csv`. Availability is computed within each formal sample by the full-mode input-diagnostics stage. The prepared input contains additional candidates and legacy columns; their presence does not mean they enter an index. The archived summaries in `reference/parameters.csv` identify actual components, direction codes and weights for every configuration and scope.

## Release boundary

No raw Reddit posts, usernames, search-response caches, provider chart exports, private data downloads, or article files are included. A code license does not settle ownership or redistribution rights for these sources. Before publishing a dataset, assess each source's terms and document permitted fields and versions separately.
