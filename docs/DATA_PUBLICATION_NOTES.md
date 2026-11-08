# Data publication notes

GitHub can host research data. Publication depends on the terms of each source, the fields included, and the intended license. Availability for download and permission to redistribute a merged dataset are separate questions. The code's MIT license does not grant rights to third-party observations.

These notes record a limited source review on 8 November 2026. They do not establish a prohibition on publishing every part of the prepared input.

## Source findings

- Alternative.me permits use of its Fear and Greed data with prominent attribution and prohibits impersonation. Its stated rules also cover data outside the API. The existing public snapshot should retain its source attribution. Source: https://alternative.me/crypto/fear-and-greed-index/
- Binance Vision's published dataset terms identify CC BY-NC-SA 4.0 and conditions for non-commercial use, attribution and derivative redistribution. These conditions differ from MIT. Review the terms applicable to the original download and retain separate source notices. This update distributes download code and archive hashes, not the source kline files. Sources: https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md and https://github.com/binance/binance-public-data
- Reddit user content remains subject to user rights and Reddit's stated data-use terms. The study used a third-party archive and derived daily scores, so the actual access route, archive terms, original content rights and proposed aggregate fields need separate consideration. A daily aggregate is different from publishing raw posts or usernames. This update publishes neither. Source: https://redditinc.com/policies/data-api-terms

## Remaining source review

Before releasing the complete combined file, document the applicable terms for Deribit DVOL, DeFiLlama stablecoin observations, Google Trends, Wikipedia pageviews, the historical GitHub export and API counts, VIX, and each public-provider series included. Record the source/version, proposed fields, relevant terms or permission, required attribution, and redistribution decision. A missing decision means permission has not been established, rather than that publication has been proved forbidden.

The complete prepared input contains raw and derived fields beyond the nine components needed for this focused diagnostic. A reduced reproduction input could omit unrelated provider indices and personal content, but still requires source review. Neither standardization nor aggregation automatically settles redistribution rights.

## Practical release boundary

Code, formulas, author-generated parameter/reference summaries and source manifests can be packaged separately from source observations. Download scripts can let a reviewer obtain permitted source files directly. Keep API keys, personal content and unauthorized private exports outside the repository.

For restricted fields, document a permitted access route where one exists. Do not promise data-on-request access unless permission and a workable delivery process have been established. For source data whose redistribution is permitted, preserve the applicable attribution and license rather than placing the entire dataset under MIT by default.
