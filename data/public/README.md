# Public study components

These are frozen extracts used in the Bitcoin sentiment-index study. They were not downloaded again for this release. They do not contain the complete analysis input.

| File | Source | Meaning |
| --- | --- | --- |
| wikipedia_pageviews.csv | Wikimedia Analytics API | Daily Bitcoin article views, English Wikipedia, all access methods, user traffic |
| google_trends_component.csv | Google Trends; author calculation | Corrected common-anchor six-query ratio |
| google_query_values.csv | Google Trends | Individual request-level query values used to reconstruct the ratio |
| google_requests.json | Archived collection metadata | Query groups, time windows, parameters, response fingerprints and recorded retrieval timestamps |
| alternative_me_cfgi.csv | Alternative.me | Published Crypto Fear & Greed Index, 0–100 |
| rolling_z_reference.csv | Author calculations from Wikimedia and Google Trends | Frozen rolling-normalization references, windows 7, 30, 60 and 90 |
| manifest.json | Package metadata | Coverage, provenance and SHA-256 fingerprints |

Data source: Google Trends (https://trends.google.com/trends/). Reuse is subject to Google terms and requires source attribution. The component and normalization are author calculations, not a Google sentiment product. Request-level values from different requests are not directly comparable before the common-anchor correction.

Data source: Alternative.me, Crypto Fear & Greed Index (https://alternative.me/crypto/fear-and-greed-index/). Retain prominent attribution when reusing or displaying these observations. Do not imply endorsement or impersonate the provider.

Wikimedia Analytics API observations are available under CC0 1.0: https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html.

Provider observations are not covered by the repository's MIT code license. See ../../docs/public-components/DATA_LICENSES.md and ../../docs/public-components/DATA_COLLECTION.md.

From the repository root, check the package offline with:

```text
python scripts/check_public_components.py
```

No third-party Python packages or full private input are required. Successful component checks do not reproduce or validate all manuscript results.
