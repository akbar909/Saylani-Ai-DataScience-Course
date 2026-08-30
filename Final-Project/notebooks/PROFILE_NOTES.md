# Verified Profiling Notes

The Phase 2 streaming probe verified the following values from the local CSVs:

| Dataset | Rows | Positive rows | Positive rate | Time range |
| --- | ---: | ---: | ---: | --- |
| `creditcard.csv` | 284,807 | 492 | 0.1727% | 0 to 172,792 |
| `PS_20174392719_1491204439457_log.csv` | 6,362,620 | 8,213 | 0.1291% | 1 to 743 |

The PaySim exploratory check read twelve 250,000-row chunks and retained a
5,000-row sample from each chunk. The sample contained 60,000 rows and 71
fraud cases. The baseline must exclude `nameOrig` and `nameDest` as direct
features. `isFlaggedFraud` is retained as a documented rule signal and should
be evaluated in an ablation comparison rather than treated as unquestioned
ground truth.

## Phase 3 training decisions

- Use stratified evaluation for the credit-card classifier.
- Use a time-aware split for PaySim because `step` is ordered.
- Report precision, recall, PR-AUC, ROC-AUC, and a confusion matrix; accuracy
  alone is not meaningful for these class ratios.
- Save preprocessing and model artifacts together so API inference uses the
  exact training transformations.

## Phase 3 baseline results

- Credit-card logistic regression: precision `0.0610`, recall `0.9184`, PR-AUC
  `0.7190`, ROC-AUC `0.9721`; confusion matrix `[[55478, 1386], [8, 90]]`.
- PaySim logistic regression: precision `0.2118`, recall `0.9383`, PR-AUC
  `0.7601`, ROC-AUC `0.9880`; confusion matrix `[[116149, 5777], [102, 1552]]`.
- Artifacts are saved in `backend/ml/artifacts/creditcard_baseline/` and
  `backend/ml/artifacts/paysim_baseline/` as `model.joblib` plus `metrics.json`.
