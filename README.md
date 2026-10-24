# Bitcoin sentiment index research code

This repository examines how component selection and weighting affect Bitcoin sentiment indices. It implements family-balanced equal weighting (EW), stress-informed component weighting (CW), and a training-only PCA comparator. Benchmark agreement, crisis interpretation, return associations and investment performance are separate questions.

## What is included

- Portable offline analysis of the corrected common-anchor Google component and frozen legacy Reddit aggregates.
- The original five sample/specification combinations across normalization windows of 7, 30, 60 and 90 observations.
- A complete component-exclusion grid: 512 configurations, each evaluated using EW, CW and PCA.
- VIX-controlled regressions, HC3 and Newey–West inference, ADF and Granger diagnostics, descriptive quantile regressions, crisis readings and fixed event windows.
- Fixed-training and monthly CW calibration, paired moving-block bootstrap comparisons and Bitcoin/cash allocation tests with transaction costs.
- Optional direct-return and risk-forecasting extensions.
- An offline public-index comparison that requires each provider's own file and source metadata.
- Archived numerical references, unit tests and implementation provenance hashes.

This is research software, not an investment recommendation or a production trading system. The historical holdout has already been examined; it is not a new untouched confirmation sample. Data-publication vintages and real-time execution feasibility are not established.

## Setup

Python 3.11 is the recommended release environment. From the repository directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

## Required frozen input

The analysis starts from a prepared daily CSV, not fresh API downloads. The required snapshot has 3,297 dates from 17 August 2017 to 26 August 2026. Its SHA-256 is recorded in `data/input_manifest.json`. A hash mismatch stops the run. The Google ratio covers 4 August 2021 onward; earlier Google-ratio values remain missing. Reddit is the frozen legacy aggregate, not a newly collected or rescored history.

**The input is not distributed in this release.** It combines third-party sources whose redistribution conditions need separate review. Obtaining an authorized copy of the identified snapshot is a prerequisite for exact numerical reproduction. There is no public download link in this version. Raw Reddit texts, API caches, manuscripts and personal documents are not included. See `DATA_DISTRIBUTION.md` for the current release boundary.

Place an authorized copy at `data/private/analysis_input.csv` or supply another location with `--input`. This directory is ignored by Git.

## Run without changing inputs or earlier results

Every output path must be a new directory. The offline analysis makes no network requests and checks that its input hash remains unchanged.

```bash
python run_analysis.py --input data/private/analysis_input.csv --output results/check-input --mode validate
python run_analysis.py --input data/private/analysis_input.csv --output results/baseline --mode baseline
python run_analysis.py --input data/private/analysis_input.csv --output results/full --mode full
```

The baseline run checks the original configurations against archived calibration parameters and investment metrics, including future-information perturbation checks. Full mode runs the component grid, statistics, monthly calibration and bootstrap. It can take substantially longer and uses four worker processes for statistical jobs. Optional extensions are requested with `--mode full --forecast-extensions` and include a large risk bootstrap. Running only baseline does not reproduce every manuscript table.

The portable full workflow, including the forecasting extensions, completed locally on 24 October 2026. Twenty-four numerical output files were compared with the archived calculations and passed the stated tolerances. Code comments and docstrings were removed in a separate release copy; its executable syntax tree is unchanged apart from docstrings. Unit tests and the baseline integration check also passed on that cleaned copy. See `VALIDATION.md` and `validation_results.json`.

## Methods and outputs

CW weights use absolute Spearman correlations with next-day absolute log returns on upper-decile stress dates. Component direction is assigned separately. Fixed chronological training ends on 31 December 2024; the common index holdout is 1 January 2025–26 August 2026. Investment returns cover 4 January 2025–26 August 2026. A and B identify different calibration histories, not independent holdout periods.

Formal regressions use unranked composite indices. Expanding percentile scores are for display and crisis descriptions. EW averages available components within each family and then available family means. CW renormalizes available weights each day. PCA uses complete cases, training-only scaling and orientation against training EW.

`reference/` contains archived author-generated summaries, not raw provider histories. Full-grid correlation summaries use common PCA-complete dates and should not be confused with available-case EW correlations. Full-mode results are exploratory across many configurations; preserve the reported multiplicity families rather than choosing the best observed specification.

## Public-index comparisons

Supply a private directory with a `providers.json` list. Each record needs `name`, `file`, `source_url` and `collection_method`. Each CSV must contain ISO `date` and numeric `value` columns, unique dates, and no missing values. Every provider needs a distinct file. Chart-read approximations and short direct collections must be labelled in the metadata.

```bash
python compare_public_indices.py --input-dir data/private/public-indices --output results/public-indices
```

These inputs are not included. Old public-index matrices and manuscript figures are not distributed as verified reference outputs in this release. This command does not automatically update a manuscript.

## Collection and data preparation

The optional Google collector documents the common-anchor procedure. A live query is a new retrieval vintage and is not guaranteed to reproduce historical observations. The legacy Reddit scoring excerpt documents the archived definition but does not regenerate the frozen snapshot. The remaining raw-source collection and merge pipeline is not yet packaged as an end-to-end public workflow. This release must not be described as reproduction from raw downloads alone.

## License and citation

Original project code is provided under MIT; see `LICENSE`. Third-party software and datasets retain their own terms. No license to redistribute third-party data is implied. Please cite the software using `CITATION.cff`; an article DOI can be added after publication. Citation is requested but is not a condition added to MIT.
