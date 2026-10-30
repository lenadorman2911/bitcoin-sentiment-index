# Reproducibility guide for reviewers

This guide points to existing code, definitions, and archived reference parameters. It adds navigation and readable extracts, not new empirical results. Benchmark alignment, sentiment validity, return associations, and investment performance are distinct assessments.

## Definitions and parameters

| Review requirement | Repository location | What it provides and its limits |
| --- | --- | --- |
| Data dictionary | [data/data_dictionary.csv](../data/data_dictionary.csv) | 182 column definitions covering the prepared input and transformed columns. Several auxiliary columns have generic descriptions; this does not establish full raw-source provenance. |
| Complete archived parameters | [reference/parameters.csv](../reference/parameters.csv) | Component directions, CW weights and calibration statistics, plus PCA parameters. Includes original and component-exclusion variants. |
| Readable original-specification weights | [CW_BASELINE_WEIGHTS.md](CW_BASELINE_WEIGHTS.md) | All five original sample/specification combinations, W = 7, 30, 60, 90, and both retrospective and fixed-training scopes: 40 groups, 440 component rows. Source-precision weights sum to one in every group. |
| Reddit additions and their numeric scores | [collectors/crypto_lexicon.py](../collectors/crypto_lexicon.py) and [REDDIT_LEXICON.md](REDDIT_LEXICON.md) | All 36 archived additions, with a readable transcription. These are scoring assumptions, not human validation of sentiment. |
| Reddit scoring and aggregation | [collectors/legacy_reddit_definition.py](../collectors/legacy_reddit_definition.py) and [collectors/README.md](../collectors/README.md) | Title plus body, VADER compound, daily unweighted mean, missingness, and archive/pagination limitations. Not a complete regeneration of the frozen aggregate. |
| Google construction | [collectors/google_common_anchor.py](../collectors/google_common_anchor.py) and [collectors/README.md](../collectors/README.md) | Common-anchor collection definition and retrieval-vintage limitations. |
| Derived market features | [collectors/feature_definitions.py](../collectors/feature_definitions.py) | Definitions of market features, including the liquidation proxy. Not an end-to-end API collection and merge pipeline. |
| Calibration and percentile scoring | [expanded_component_tests.py](../expanded_component_tests.py) | Absolute stress-period correlations determine weight strength; direction codes are separate. Expanding ranks times 100 provide descriptive scores, not probabilities. |
| Numerical reference checks | [VALIDATION.md](../VALIDATION.md) and [validation_results.json](../validation_results.json) | Author-reported validation on the identified frozen input. This guide does not rerun those empirical checks. |
| Data access boundary | [DATA_DISTRIBUTION.md](../DATA_DISTRIBUTION.md), [DATA_SOURCES.md](../DATA_SOURCES.md), and [data/input_manifest.json](../data/input_manifest.json) | Required input identity, sources, and redistribution restrictions. Exact reproduction requires authorized access to the complete prepared input. |

## Interpretation of the weights and components

CW uses absolute Spearman correlations with next-day absolute log returns on stress-related dates. A large weight indicates association with movement magnitude; it does not identify optimism, pessimism, or a causal mechanism. Fear-greed direction is imposed separately.

Wikipedia pageviews and GitHub commits retain positive direction codes as attention/activity assumptions. The readable component labels do not validate those signs. The BTC-to-ETH price ratio is not Bitcoin market-capitalization dominance. The absolute-return-volume proxy is not observed liquidation data.

Formal return tests use unranked indices. Expanding percentile scores rank the current value against available history and are used for display and crisis interpretation. For baseline CW, retrospective sample-specific weights are applied to longer component history before ranking; an expanding rank does not turn those baseline weights into real-time estimates.

## What this documentation does not establish

The complete merged empirical input is not provided by this documentation. It does not resolve source redistribution permissions, supply actual liquidation or market-cap-dominance data, validate Wikipedia/GitHub signs, repair chart-estimated CoinGlass histories, or add a signed-order-flow crisis replacement test. The historical holdout has already been examined, and source publication vintages and real-time execution feasibility remain separate limitations.

## Checking these extracts

The accompanying `DOCUMENTATION_AUDIT.json` records SHA-256 identities of the existing source files used for the readable extracts, row counts, and the maximum CW group-sum error. It is a documentation check, not independent replication of the article's empirical results.
