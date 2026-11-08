# Spot crisis reproduction update

This additive update packages the historical spot taker-buy diagnostic in the revised Bitcoin sentiment article. Copy the `reproduction/spot_crisis/` directory and the three new `docs/` files into the repository. No existing analysis script needs replacement.

Start with [the reproduction instructions](docs/SPOT_CRISIS_REPRODUCTION.md). The package reproduces six reduced-index CW scores and checks 26 component weights against archived results. It uses the existing authorized frozen input and checksum-verified Binance spot archives.

Additional documentation:

- [Current manuscript results and commands](docs/MANUSCRIPT_RESULTS_MAP.md)
- [Source data publication notes](docs/DATA_PUBLICATION_NOTES.md)

After adding these files, append a link to `docs/SPOT_CRISIS_REPRODUCTION.md` in the main README and reviewer guide. Explain there that the added spot diagnostic covers LUNA and FTX, uses retrospective refitted weights, and is separate from the retained baseline futures taker-buy component. The old statement that the documentation does not add a crisis replacement should be read in its earlier version context and updated to reference the new extension.

The software release v0.1.1, public-component release v0.1.2, and documentation commit 8e0b45e remain historical records. Create a new release only after the added files have been committed and checked, and cite that new tag/commit for this extension. This folder is an upload package and does not assert that a new release has already been published.

The complete prepared input and raw source archives are excluded. Their hashes and access requirements are documented. Original project code is covered by the repository MIT license. Dataset terms remain source-specific.
