# CW weights for the original specifications

This is a readable extract of the existing `reference/parameters.csv`, filtered to `mask = 0`. It does not re-estimate weights or change empirical results. The source CSV remains authoritative and also includes component-exclusion variants.

Each row below is a nominal component weight before daily renormalization for missing observations. Direction is a separately imposed construction code, not the sign of an estimated sentiment effect. Percentages are rounded for display.

The extract has 40 specification/scope/window groups and 440 component rows. Each group sums to one in source precision. All five original sample/specification combinations appear for W = 7, 30, 60, and 90 under each of the two scopes. Monthly recalibration sequences are not represented by these fixed-weight tables.

`retrospective_full_sample` uses the sample-specific calibration history. `fixed_training_holdout` identifies fixed training-period weights, with training ending on 31 December 2024. The A and B histories share the same later holdout and are not independent holdout samples.

## sample_a_2021_plus / baseline_all_families / fixed_training_holdout / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 13.406517 |
| 30-day realized volatility | -1 | 11.063373 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 7.097535 |
| USD trading-volume proxy | +1 | 16.266919 |
| USDT share of stablecoin capitalization | -1 | 2.378040 |
| Funding-rate z-score | +1 | 6.014612 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 11.316656 |
| Deribit Bitcoin implied volatility | -1 | 10.044616 |
| Google Trends greed-fear measure | +1 | 12.862241 |
| Bitcoin Wikipedia pageviews | +1 | 8.151189 |
| Frozen legacy Reddit mean VADER compound score | +1 | 0.406377 |
| Bitcoin Core commit count | +1 | 0.991926 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / fixed_training_holdout / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.955651 |
| 30-day realized volatility | -1 | 8.134937 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 5.738942 |
| USD trading-volume proxy | +1 | 20.630414 |
| USDT share of stablecoin capitalization | -1 | 1.846959 |
| Funding-rate z-score | +1 | 5.966962 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 16.366447 |
| Deribit Bitcoin implied volatility | -1 | 12.261892 |
| Google Trends greed-fear measure | +1 | 10.823333 |
| Bitcoin Wikipedia pageviews | +1 | 5.077238 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.780208 |
| Bitcoin Core commit count | +1 | 1.417016 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / fixed_training_holdout / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.911926 |
| 30-day realized volatility | -1 | 2.596490 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 5.375339 |
| USD trading-volume proxy | +1 | 22.259945 |
| USDT share of stablecoin capitalization | -1 | 0.375319 |
| Funding-rate z-score | +1 | 9.660766 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 18.402318 |
| Deribit Bitcoin implied volatility | -1 | 10.669674 |
| Google Trends greed-fear measure | +1 | 11.588254 |
| Bitcoin Wikipedia pageviews | +1 | 4.473087 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.189799 |
| Bitcoin Core commit count | +1 | 1.497083 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / fixed_training_holdout / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.340241 |
| 30-day realized volatility | -1 | 2.217235 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 5.862461 |
| USD trading-volume proxy | +1 | 23.798356 |
| USDT share of stablecoin capitalization | -1 | 0.533517 |
| Funding-rate z-score | +1 | 6.564010 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 22.268527 |
| Deribit Bitcoin implied volatility | -1 | 9.492497 |
| Google Trends greed-fear measure | +1 | 10.021403 |
| Bitcoin Wikipedia pageviews | +1 | 2.554997 |
| Frozen legacy Reddit mean VADER compound score | +1 | 6.680558 |
| Bitcoin Core commit count | +1 | 2.666199 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / retrospective_full_sample / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 9.086396 |
| 30-day realized volatility | -1 | 15.569648 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 6.335620 |
| USD trading-volume proxy | +1 | 11.009208 |
| USDT share of stablecoin capitalization | -1 | 4.643954 |
| Funding-rate z-score | +1 | 1.106165 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 12.554499 |
| Deribit Bitcoin implied volatility | -1 | 17.416849 |
| Google Trends greed-fear measure | +1 | 8.400139 |
| Bitcoin Wikipedia pageviews | +1 | 12.514089 |
| Frozen legacy Reddit mean VADER compound score | +1 | 0.613339 |
| Bitcoin Core commit count | +1 | 0.750094 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / retrospective_full_sample / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 5.606347 |
| 30-day realized volatility | -1 | 10.077399 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 8.936979 |
| USD trading-volume proxy | +1 | 13.557005 |
| USDT share of stablecoin capitalization | -1 | 1.253949 |
| Funding-rate z-score | +1 | 1.986492 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 12.710714 |
| Deribit Bitcoin implied volatility | -1 | 15.344619 |
| Google Trends greed-fear measure | +1 | 11.662776 |
| Bitcoin Wikipedia pageviews | +1 | 11.980898 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.107889 |
| Bitcoin Core commit count | +1 | 2.774933 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / retrospective_full_sample / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.550134 |
| 30-day realized volatility | -1 | 3.287514 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 9.958841 |
| USD trading-volume proxy | +1 | 17.537543 |
| USDT share of stablecoin capitalization | -1 | 0.377110 |
| Funding-rate z-score | +1 | 1.240727 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 15.473754 |
| Deribit Bitcoin implied volatility | -1 | 12.011723 |
| Google Trends greed-fear measure | +1 | 12.940180 |
| Bitcoin Wikipedia pageviews | +1 | 12.694209 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.867862 |
| Bitcoin Core commit count | +1 | 2.060404 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / baseline_all_families / retrospective_full_sample / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.471045 |
| 30-day realized volatility | -1 | 1.227802 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 8.166855 |
| USD trading-volume proxy | +1 | 18.242845 |
| USDT share of stablecoin capitalization | -1 | 0.055927 |
| Funding-rate z-score | +1 | 3.397370 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 17.662546 |
| Deribit Bitcoin implied volatility | -1 | 10.380167 |
| Google Trends greed-fear measure | +1 | 12.204261 |
| Bitcoin Wikipedia pageviews | +1 | 12.033128 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.011022 |
| Bitcoin Core commit count | +1 | 4.147031 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / fixed_training_holdout / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 18.460144 |
| 30-day realized volatility | -1 | 15.233746 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 9.772972 |
| USD trading-volume proxy | +1 | 22.398784 |
| USDT share of stablecoin capitalization | -1 | 3.274449 |
| Google Trends greed-fear measure | +1 | 17.710702 |
| Bitcoin Wikipedia pageviews | +1 | 11.223805 |
| Frozen legacy Reddit mean VADER compound score | +1 | 0.559563 |
| Bitcoin Core commit count | +1 | 1.365835 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / fixed_training_holdout / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 12.163730 |
| 30-day realized volatility | -1 | 12.437848 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 8.774510 |
| USD trading-volume proxy | +1 | 31.542710 |
| USDT share of stablecoin capitalization | -1 | 2.823894 |
| Google Trends greed-fear measure | +1 | 16.548250 |
| Bitcoin Wikipedia pageviews | +1 | 7.762803 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.779720 |
| Bitcoin Core commit count | +1 | 2.166536 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / fixed_training_holdout / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 12.913794 |
| 30-day realized volatility | -1 | 4.237974 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 8.773593 |
| USD trading-volume proxy | +1 | 36.332539 |
| USDT share of stablecoin capitalization | -1 | 0.612594 |
| Google Trends greed-fear measure | +1 | 18.914275 |
| Bitcoin Wikipedia pageviews | +1 | 7.300945 |
| Frozen legacy Reddit mean VADER compound score | +1 | 8.470757 |
| Bitcoin Core commit count | +1 | 2.443529 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / fixed_training_holdout / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 11.901491 |
| 30-day realized volatility | -1 | 3.595032 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 9.505415 |
| USD trading-volume proxy | +1 | 38.586736 |
| USDT share of stablecoin capitalization | -1 | 0.865046 |
| Google Trends greed-fear measure | +1 | 16.248737 |
| Bitcoin Wikipedia pageviews | +1 | 4.142680 |
| Frozen legacy Reddit mean VADER compound score | +1 | 10.831880 |
| Bitcoin Core commit count | +1 | 4.322984 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / retrospective_full_sample / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 13.183499 |
| 30-day realized volatility | -1 | 22.590084 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 9.192385 |
| USD trading-volume proxy | +1 | 15.973319 |
| USDT share of stablecoin capitalization | -1 | 6.737938 |
| Google Trends greed-fear measure | +1 | 12.187805 |
| Bitcoin Wikipedia pageviews | +1 | 18.156758 |
| Frozen legacy Reddit mean VADER compound score | +1 | 0.889897 |
| Bitcoin Core commit count | +1 | 1.088316 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / retrospective_full_sample / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 8.013855 |
| 30-day realized volatility | -1 | 14.404891 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 12.774746 |
| USD trading-volume proxy | +1 | 19.378729 |
| USDT share of stablecoin capitalization | -1 | 1.792427 |
| Google Trends greed-fear measure | +1 | 16.671069 |
| Bitcoin Wikipedia pageviews | +1 | 17.125801 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.871922 |
| Bitcoin Core commit count | +1 | 3.966560 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / retrospective_full_sample / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 10.593141 |
| 30-day realized volatility | -1 | 4.612515 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 13.972654 |
| USD trading-volume proxy | +1 | 24.605878 |
| USDT share of stablecoin capitalization | -1 | 0.529100 |
| Google Trends greed-fear measure | +1 | 18.155592 |
| Bitcoin Wikipedia pageviews | +1 | 17.810485 |
| Frozen legacy Reddit mean VADER compound score | +1 | 6.829806 |
| Bitcoin Core commit count | +1 | 2.890830 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_a_2021_plus / market_behavioral / retrospective_full_sample / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 10.897103 |
| 30-day realized volatility | -1 | 1.790845 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.911997 |
| USD trading-volume proxy | +1 | 26.608617 |
| USDT share of stablecoin capitalization | -1 | 0.081574 |
| Google Trends greed-fear measure | +1 | 17.800869 |
| Bitcoin Wikipedia pageviews | +1 | 17.551258 |
| Frozen legacy Reddit mean VADER compound score | +1 | 7.308968 |
| Bitcoin Core commit count | +1 | 6.048769 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / fixed_training_holdout / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 3.003410 |
| 30-day realized volatility | -1 | 5.770423 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 0.081383 |
| USD trading-volume proxy | +1 | 15.598357 |
| USDT share of stablecoin capitalization | -1 | 7.498837 |
| Funding-rate z-score | +1 | 15.637111 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 11.777244 |
| Deribit Bitcoin implied volatility | -1 | 6.491242 |
| Google Trends greed-fear measure | +1 | 4.235777 |
| Bitcoin Wikipedia pageviews | +1 | 15.947140 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.615408 |
| Bitcoin Core commit count | +1 | 8.343668 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / fixed_training_holdout / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 6.056466 |
| 30-day realized volatility | -1 | 3.535136 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.372352 |
| USD trading-volume proxy | +1 | 15.854185 |
| USDT share of stablecoin capitalization | -1 | 4.695139 |
| Funding-rate z-score | +1 | 15.835011 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 10.849871 |
| Deribit Bitcoin implied volatility | -1 | 10.706068 |
| Google Trends greed-fear measure | +1 | 1.095293 |
| Bitcoin Wikipedia pageviews | +1 | 15.767903 |
| Frozen legacy Reddit mean VADER compound score | +1 | 2.969514 |
| Bitcoin Core commit count | +1 | 1.263062 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / fixed_training_holdout / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.819848 |
| 30-day realized volatility | -1 | 7.253575 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.951723 |
| USD trading-volume proxy | +1 | 10.152126 |
| USDT share of stablecoin capitalization | -1 | 10.977541 |
| Funding-rate z-score | +1 | 19.342067 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 9.110759 |
| Deribit Bitcoin implied volatility | -1 | 5.813898 |
| Google Trends greed-fear measure | +1 | 0.957386 |
| Bitcoin Wikipedia pageviews | +1 | 11.711777 |
| Frozen legacy Reddit mean VADER compound score | +1 | 2.401862 |
| Bitcoin Core commit count | +1 | 2.507438 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / fixed_training_holdout / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 6.651005 |
| 30-day realized volatility | -1 | 10.429928 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.566636 |
| USD trading-volume proxy | +1 | 8.788017 |
| USDT share of stablecoin capitalization | -1 | 11.511064 |
| Funding-rate z-score | +1 | 14.921188 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 11.117005 |
| Deribit Bitcoin implied volatility | -1 | 7.333030 |
| Google Trends greed-fear measure | +1 | 1.755582 |
| Bitcoin Wikipedia pageviews | +1 | 9.813580 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.867334 |
| Bitcoin Core commit count | +1 | 2.245630 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / retrospective_full_sample / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 9.049951 |
| 30-day realized volatility | -1 | 17.773672 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 10.449647 |
| USD trading-volume proxy | +1 | 3.559679 |
| USDT share of stablecoin capitalization | -1 | 4.861164 |
| Funding-rate z-score | +1 | 3.289767 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 10.025892 |
| Deribit Bitcoin implied volatility | -1 | 5.383131 |
| Google Trends greed-fear measure | +1 | 4.422299 |
| Bitcoin Wikipedia pageviews | +1 | 14.487339 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.213491 |
| Bitcoin Core commit count | +1 | 11.483967 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / retrospective_full_sample / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 1.121438 |
| 30-day realized volatility | -1 | 17.806676 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 8.473612 |
| USD trading-volume proxy | +1 | 5.959268 |
| USDT share of stablecoin capitalization | -1 | 2.500119 |
| Funding-rate z-score | +1 | 4.954597 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 13.487482 |
| Deribit Bitcoin implied volatility | -1 | 5.192280 |
| Google Trends greed-fear measure | +1 | 7.483759 |
| Bitcoin Wikipedia pageviews | +1 | 22.186329 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.431884 |
| Bitcoin Core commit count | +1 | 7.402556 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / retrospective_full_sample / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 2.978088 |
| 30-day realized volatility | -1 | 10.740491 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 15.438557 |
| USD trading-volume proxy | +1 | 7.933026 |
| USDT share of stablecoin capitalization | -1 | 1.586855 |
| Funding-rate z-score | +1 | 7.219910 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 12.539843 |
| Deribit Bitcoin implied volatility | -1 | 5.088686 |
| Google Trends greed-fear measure | +1 | 7.873027 |
| Bitcoin Wikipedia pageviews | +1 | 17.754153 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.113074 |
| Bitcoin Core commit count | +1 | 6.734291 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families / retrospective_full_sample / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 2.326438 |
| 30-day realized volatility | -1 | 12.324343 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 14.798893 |
| USD trading-volume proxy | +1 | 7.521910 |
| USDT share of stablecoin capitalization | -1 | 1.036060 |
| Funding-rate z-score | +1 | 5.962040 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 16.205594 |
| Deribit Bitcoin implied volatility | -1 | 7.080464 |
| Google Trends greed-fear measure | +1 | 6.125324 |
| Bitcoin Wikipedia pageviews | +1 | 15.451307 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.009132 |
| Bitcoin Core commit count | +1 | 7.158494 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / fixed_training_holdout / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 2.706856 |
| 30-day realized volatility | -1 | 5.200657 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 0.073347 |
| USD trading-volume proxy | +1 | 14.058189 |
| USDT share of stablecoin capitalization | -1 | 6.758409 |
| Funding-rate z-score | +1 | 14.093116 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 10.614369 |
| Deribit Bitcoin implied volatility | -1 | 5.850302 |
| Futures taker-buy volume share | +1 | 9.873913 |
| Google Trends greed-fear measure | +1 | 3.817540 |
| Bitcoin Wikipedia pageviews | +1 | 14.372533 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.060948 |
| Bitcoin Core commit count | +1 | 7.519821 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / fixed_training_holdout / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 5.571848 |
| 30-day realized volatility | -1 | 3.252266 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 10.462373 |
| USD trading-volume proxy | +1 | 14.585584 |
| USDT share of stablecoin capitalization | -1 | 4.319450 |
| Funding-rate z-score | +1 | 14.567945 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 9.981699 |
| Deribit Bitcoin implied volatility | -1 | 9.849404 |
| Futures taker-buy volume share | +1 | 8.001676 |
| Google Trends greed-fear measure | +1 | 1.007651 |
| Bitcoin Wikipedia pageviews | +1 | 14.506207 |
| Frozen legacy Reddit mean VADER compound score | +1 | 2.731903 |
| Bitcoin Core commit count | +1 | 1.161996 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / fixed_training_holdout / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 7.602013 |
| 30-day realized volatility | -1 | 7.051514 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.618786 |
| USD trading-volume proxy | +1 | 9.869320 |
| USDT share of stablecoin capitalization | -1 | 10.671742 |
| Funding-rate z-score | +1 | 18.803260 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 8.856963 |
| Deribit Bitcoin implied volatility | -1 | 5.651941 |
| Futures taker-buy volume share | +1 | 2.785679 |
| Google Trends greed-fear measure | +1 | 0.930716 |
| Bitcoin Wikipedia pageviews | +1 | 11.385524 |
| Frozen legacy Reddit mean VADER compound score | +1 | 2.334954 |
| Bitcoin Core commit count | +1 | 2.437589 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / fixed_training_holdout / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 6.450236 |
| 30-day realized volatility | -1 | 10.115087 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.217482 |
| USD trading-volume proxy | +1 | 8.522738 |
| USDT share of stablecoin capitalization | -1 | 11.163587 |
| Funding-rate z-score | +1 | 14.470772 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 10.781423 |
| Deribit Bitcoin implied volatility | -1 | 7.111673 |
| Futures taker-buy volume share | +1 | 3.018637 |
| Google Trends greed-fear measure | +1 | 1.702588 |
| Bitcoin Wikipedia pageviews | +1 | 9.517344 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.750593 |
| Bitcoin Core commit count | +1 | 2.177843 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / retrospective_full_sample / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 8.637427 |
| 30-day realized volatility | -1 | 16.963496 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 9.973321 |
| USD trading-volume proxy | +1 | 3.397419 |
| USDT share of stablecoin capitalization | -1 | 4.639577 |
| Funding-rate z-score | +1 | 3.139810 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 9.568882 |
| Deribit Bitcoin implied volatility | -1 | 5.137752 |
| Futures taker-buy volume share | +1 | 4.558296 |
| Google Trends greed-fear measure | +1 | 4.220718 |
| Bitcoin Wikipedia pageviews | +1 | 13.826963 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.975845 |
| Bitcoin Core commit count | +1 | 10.960493 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / retrospective_full_sample / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 1.052602 |
| 30-day realized volatility | -1 | 16.713678 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 7.953490 |
| USD trading-volume proxy | +1 | 5.593480 |
| USDT share of stablecoin capitalization | -1 | 2.346658 |
| Funding-rate z-score | +1 | 4.650477 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 12.659601 |
| Deribit Bitcoin implied volatility | -1 | 4.873571 |
| Futures taker-buy volume share | +1 | 6.138140 |
| Google Trends greed-fear measure | +1 | 7.024396 |
| Bitcoin Wikipedia pageviews | +1 | 20.824501 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.221230 |
| Bitcoin Core commit count | +1 | 6.948177 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / retrospective_full_sample / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 2.871057 |
| 30-day realized volatility | -1 | 10.354483 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 14.883703 |
| USD trading-volume proxy | +1 | 7.647917 |
| USDT share of stablecoin capitalization | -1 | 1.529824 |
| Funding-rate z-score | +1 | 6.960430 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 12.089168 |
| Deribit Bitcoin implied volatility | -1 | 4.905802 |
| Futures taker-buy volume share | +1 | 3.593947 |
| Google Trends greed-fear measure | +1 | 7.590074 |
| Bitcoin Wikipedia pageviews | +1 | 17.116078 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.965252 |
| Bitcoin Core commit count | +1 | 6.492264 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / baseline_all_families_with_taker / retrospective_full_sample / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 2.254752 |
| 30-day realized volatility | -1 | 11.944584 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 14.342884 |
| USD trading-volume proxy | +1 | 7.290131 |
| USDT share of stablecoin capitalization | -1 | 1.004135 |
| Funding-rate z-score | +1 | 5.778327 |
| Absolute-return times BTC-volume proxy (not actual liquidations) | -1 | 15.706238 |
| Deribit Bitcoin implied volatility | -1 | 6.862289 |
| Futures taker-buy volume share | +1 | 3.081376 |
| Google Trends greed-fear measure | +1 | 5.936580 |
| Bitcoin Wikipedia pageviews | +1 | 14.975194 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.885596 |
| Bitcoin Core commit count | +1 | 6.937914 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / fixed_training_holdout / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 4.544122 |
| 30-day realized volatility | -1 | 8.730578 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 0.123131 |
| USD trading-volume proxy | +1 | 23.600117 |
| USDT share of stablecoin capitalization | -1 | 11.345646 |
| Google Trends greed-fear measure | +1 | 6.408678 |
| Bitcoin Wikipedia pageviews | +1 | 24.127822 |
| Frozen legacy Reddit mean VADER compound score | +1 | 8.496042 |
| Bitcoin Core commit count | +1 | 12.623864 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / fixed_training_holdout / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 9.673468 |
| 30-day realized volatility | -1 | 5.646365 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 18.164070 |
| USD trading-volume proxy | +1 | 25.322513 |
| USDT share of stablecoin capitalization | -1 | 7.499139 |
| Google Trends greed-fear measure | +1 | 1.749416 |
| Bitcoin Wikipedia pageviews | +1 | 25.184703 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.742947 |
| Bitcoin Core commit count | +1 | 2.017379 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / fixed_training_holdout / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 11.896331 |
| 30-day realized volatility | -1 | 11.034860 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 18.182150 |
| USD trading-volume proxy | +1 | 15.444424 |
| USDT share of stablecoin capitalization | -1 | 16.700128 |
| Google Trends greed-fear measure | +1 | 1.456470 |
| Bitcoin Wikipedia pageviews | +1 | 17.817120 |
| Frozen legacy Reddit mean VADER compound score | +1 | 3.653951 |
| Bitcoin Core commit count | +1 | 3.814565 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / fixed_training_holdout / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 9.982181 |
| 30-day realized volatility | -1 | 15.653789 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 17.359821 |
| USD trading-volume proxy | +1 | 13.189521 |
| USDT share of stablecoin capitalization | -1 | 17.276415 |
| Google Trends greed-fear measure | +1 | 2.634871 |
| Bitcoin Wikipedia pageviews | +1 | 14.728741 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.804299 |
| Bitcoin Core commit count | +1 | 3.370361 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / retrospective_full_sample / W = 7

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 11.131385 |
| 30-day realized volatility | -1 | 21.861510 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 12.853004 |
| USD trading-volume proxy | +1 | 4.378384 |
| USDT share of stablecoin capitalization | -1 | 5.979202 |
| Google Trends greed-fear measure | +1 | 5.439401 |
| Bitcoin Wikipedia pageviews | +1 | 17.819340 |
| Frozen legacy Reddit mean VADER compound score | +1 | 6.412563 |
| Bitcoin Core commit count | +1 | 14.125210 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / retrospective_full_sample / W = 30

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 1.468511 |
| 30-day realized volatility | -1 | 23.317655 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 11.096105 |
| USD trading-volume proxy | +1 | 7.803598 |
| USDT share of stablecoin capitalization | -1 | 3.273879 |
| Google Trends greed-fear measure | +1 | 9.799904 |
| Bitcoin Wikipedia pageviews | +1 | 29.052764 |
| Frozen legacy Reddit mean VADER compound score | +1 | 4.494016 |
| Bitcoin Core commit count | +1 | 9.693569 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / retrospective_full_sample / W = 60

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 3.962776 |
| 30-day realized volatility | -1 | 14.291773 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 20.543229 |
| USD trading-volume proxy | +1 | 10.556036 |
| USDT share of stablecoin capitalization | -1 | 2.111540 |
| Google Trends greed-fear measure | +1 | 10.476198 |
| Bitcoin Wikipedia pageviews | +1 | 23.624464 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.473038 |
| Bitcoin Core commit count | +1 | 8.960946 |

Source group weight sum: 1.000000000000 (within numerical precision).

## sample_b_2023_plus / market_behavioral / retrospective_full_sample / W = 90

| Component | Code | Weight (%) |
| --- | ---: | ---: |
| Seven-day momentum | +1 | 3.288164 |
| 30-day realized volatility | -1 | 17.419098 |
| BTC-to-ETH price ratio (not market-cap dominance) | -1 | 20.916601 |
| USD trading-volume proxy | +1 | 10.631389 |
| USDT share of stablecoin capitalization | -1 | 1.464356 |
| Google Trends greed-fear measure | +1 | 8.657469 |
| Bitcoin Wikipedia pageviews | +1 | 21.838717 |
| Frozen legacy Reddit mean VADER compound score | +1 | 5.666466 |
| Bitcoin Core commit count | +1 | 10.117741 |

Source group weight sum: 1.000000000000 (within numerical precision).
