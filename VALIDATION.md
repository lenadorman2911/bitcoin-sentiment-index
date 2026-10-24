# Validation status

- Original-configuration integration: passed locally on the hash-identified frozen input.
- Calibration and PCA parameters: checked against archived mask-zero reference rows.
- Investment metrics: checked against archived EW/CW/PCA baseline results.
- Post-cutoff perturbation of features and returns: fixed calibration unchanged.
- Unit tests: run with `python -m unittest discover -s tests -v`.
- Full 512-configuration portable workflow: completed, including the direct-return and risk-forecasting extensions.
- Archived-output comparison: 24 files, 989,154 rows; no numeric differences. Numeric comparison tolerances were absolute 1e-10 and relative 1e-8.
- Comment cleanup: 25 comments and 30 docstrings removed from 21 Python files. Executable syntax trees were compared before and after; only docstrings differ. The full run used the pre-cleanup portable copy; unit tests and a baseline run were repeated on the cleaned release.
- Live data collection: not executed during release preparation.
- Public-provider historical data provenance: not established by unit tests.

The data file itself is not included. Continuous integration uses synthetic inputs only, so CI passing does not establish reproduction of the manuscript's empirical numbers. The local full comparison used the archived prepared input. It does not establish independent validation from raw downloads, external-provider provenance or real-time data availability.
