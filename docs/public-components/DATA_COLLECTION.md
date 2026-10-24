# Frozen data and component construction

## Scope and provenance

All three headline series are extracted from the unchanged frozen study input. Its SHA-256 is recorded in data/public/manifest.json. Extracts retain the saved decimal strings. There was no new network collection for this package. Checks against retained local Wikipedia and Alternative.me files establish local agreement, not independent provider verification. Exact original retrieval timestamps for these two sources were not retained here.

Dates use YYYY-MM-DD. Empty normalization fields mean unavailable, never zero. Google and CFGI files contain only their observed history. The normalization reference retains the full 3,297-day study calendar.

## Wikipedia

Coverage: 2017-08-17 through 2026-08-26, 3,297 daily values. Archived collectors specify project en.wikipedia, article Bitcoin, access all-access, agent user, granularity daily. Endpoint pattern:

https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Bitcoin/daily/{start}/{end}

Counts measure attention, not the emotional direction of that attention. Original HTTP responses are not included. A fresh download may contain revisions.

## Corrected Google component

Coverage: 2021-08-04 through 2026-08-26, 1,849 daily ratios. No earlier Google values are imputed. The archived collector used pytrends 4.9.2, worldwide geography, category 0, web search, hl=en-US and tz=0. Requests use up to 180 days with 14-day overlaps.

Greed-labelled queries: buy bitcoin; bitcoin price prediction; bitcoin ath.

Fear-labelled queries: sell bitcoin; bitcoin crash; is bitcoin dead.

The common anchor is buy bitcoin, present in both requests. For each day and paired request window:

G = mean(three greed query values) / anchor in the greed request

F = mean(three fear query values) / anchor in the fear request

ratio = (G - F) / (G + F)

Each request has its own Google 0–100 scale. Dividing by the same anchor within each request corrects independent multiplicative request scaling. The ratio is in [-1, 1], not [0, 100]. It does not validate the emotional labels, eliminate rounding or establish predictive value. Missing responses, partial days, nonpositive anchors or a nonpositive total produce missing values. For overlap dates the earliest request window is retained, as in the study collector.

google_query_values.csv preserves all overlapping request values, not just the selected day. google_requests.json supplies request metadata and archived payload fingerprints. Recorded retrieval timestamps are metadata from the saved responses, not independently certified timestamps or historical real-time vintages. Later downloads need not reproduce them. The offline checker reconstructs the saved request payloads and verifies their fingerprints before computing the ratio.

## Alternative.me CFGI

Coverage: 2018-02-01 through 2026-08-26, 3,126 observed values, as retained in the study input. Three dates are absent: 2018-04-14, 2018-04-15 and 2018-04-16. They are not filled. The collector used the official /fng/ API and converted Unix timestamps to dates. The file includes published index values only. Classifications and provider methodology are not reconstructed. CFGI is an external reference, not observed true sentiment.

## Rolling normalization

For Wikipedia and the Google ratio, z(t,W) = [x(t) - mean(x(t-W+1:t))] / sample_sd(x(t-W+1:t)). Windows include the current day and require W available observations. W is 7, 30, 60 or 90. The standard deviation uses W-1 in its denominator. Incomplete windows and zero variance remain missing. There is no filling or smoothing. The offline checker compares an independent calculation with the frozen reference at absolute tolerance 1e-8. CFGI is supplied on its original published scale and is not normalized by this package.

## Reproduction boundary

These files permit offline reconstruction of the corrected Google ratio and checking the two released component normalizations. They cannot reproduce complete EW, CW, PCA, investment tests or all manuscript tables because other required sources are not included. The existing full-input hash requirement and analysis code are unchanged.
