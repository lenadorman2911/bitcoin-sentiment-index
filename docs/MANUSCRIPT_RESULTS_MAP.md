# Manuscript result map

This map uses the revised article's five main exhibits and Supplemental Material Appendices A–E, as reviewed on 8 November 2026. It links current results to calculations. Numerical commands require the hash-identified prepared input described in the main README.

From the repository root, choose new output directories:

```sh
python run_analysis.py --input data/private/analysis_input.csv --output results/baseline-check --mode baseline
python run_analysis.py --input data/private/analysis_input.csv --output results/full-check --mode full
```

The full calculation is larger than the baseline check. This update validates the added spot-crisis extension. It does not report a new execution of the entire pre-existing statistical suite.

| Article result | Calculation and output | Selection and scope |
| --- | --- | --- |
| Exhibit 1 component directions and interpretation | `scripts/build_cw_index_versions.py`, `reference/parameters.csv`, `docs/CW_BASELINE_WEIGHTS.md` | Construction settings and archived parameters. Narrative rationale and limitations are author interpretation. |
| Exhibit 2 index paths during Sample A | Full command, `results/full-check/expanded/baseline_daily_indices.csv` | Full-index Sample A, W=90. Percentile display requires the full available history. The command supplies numerical series rather than a formatted manuscript figure. |
| Exhibit 3 overlapping 30-day return inference | Full command, `results/full-check/expanded/statistical_tests.csv` | Retrospective full sample, original component set, full index, EW, forward 30-day horizon, VIX control, HAC observation lags 30. Select W=60/90 and Sample A/B. Preserve the complete coefficient/SE/CI conventions. |
| Exhibit 4 original full and reduced readings | Baseline command, `results/baseline-check/crisis_readings.csv` | Sample A, W=90, EW/CW, LUNA/FTX, full and reduced constructions. |
| Exhibit 4 reduced CW volume-excluded readings and spot paragraph | Added command in `SPOT_CRISIS_REPRODUCTION.md`, `results/spot-crisis-check/crisis_readings.csv` | CW, reduced components, W=90, original/excluded/replaced volume. This extension covers six CW scores. The EW exclusion rows remain part of the broader component-exclusion calculation. |
| Exhibit 5 holdout benchmark comparisons | Baseline command, `results/baseline-check/benchmark_correlations.csv` | `scope=fixed_training_holdout`, W=90, EW/CW/PCA/momentum-volatility, five original sample/specification combinations. Do not replace available-case correlations with full-grid PCA-complete-case summaries. |
| Allocation returns and cost sensitivity | Baseline `investment_metrics.csv`; full `expanded/strategy_metrics_all_sensitivities.csv` | Primary full index, calibration history A, W=90, contrarian median rule, lag two, cost 10 basis points. Full output supplies other cost/lag settings. |
| Direct test of period coefficient differences | Full command, `results/full-check/period_stability/slope_change_results.csv` | Full EW, W=90, VIX control, split 10 July 2023, HAC30 observation lags. Preserve exclusion of forward horizons crossing the split. |
| Supplemental D5 full-sample EW benchmark grid | Baseline `benchmark_correlations.csv` | `scope=retrospective_full_sample`, `method=ew`, windows 7/30/60/90. |
| Supplemental D6 CW minus EW grid | Baseline `benchmark_correlations.csv` | Join CW and EW on sample, specification, window and scope, then subtract Pearson correlations. These are descriptive full-sample differences. |
| Supplemental E spot-volume construction and six CW crisis results | `reproduction/spot_crisis/collect.py`, `reproduction/spot_crisis/reproduce.py` | Pinned spot archives and exact prepared-input hash. Retrospective Sample A weights refitted for each variant. |

Public-provider correlations in Appendix A require each provider's distinct input and source metadata through `compare_public_indices.py`. Chart-estimated values remain approximate. This extension does not distribute those provider histories or regenerate Appendix A from raw downloads.

Event timing, candidate screening and other diagnostics are described by the existing analysis code and documentation. The map above covers the primary article results and the newly packaged diagnostic. Table and figure formatting remains a separate manuscript step.
