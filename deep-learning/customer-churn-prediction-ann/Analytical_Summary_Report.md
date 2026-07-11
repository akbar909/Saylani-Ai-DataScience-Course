# Analytical Summary Report
## Customer Churn Prediction using an Artificial Neural Network (ANN)

**Dataset:** IBM Telco Customer Churn (`WA_Fn-UseC_-Telco-Customer-Churn.csv`) — 7,043 customer records, 21 attributes
**Framework:** TensorFlow / Keras (Sequential API), Scikit-Learn

---

## 1. Data Preprocessing Actions

The raw dataset required several corrective and encoding steps before it could be consumed by a neural network, which — unlike tree-based models — cannot handle missing values, string types, or unscaled numeric ranges natively.

**Missing value strategy.** No column reported missing values under a naive `df.isnull().sum()` check, because `TotalCharges` was stored as an `object` (string) dtype rather than numeric. On inspection, 11 rows contained blank-string values in this column, all corresponding to customers with `tenure = 0` — i.e., brand-new customers who had not yet been billed a cumulative amount. This is a case of *structurally missing data*, not random noise, since it is fully explained by tenure. The column was coerced to numeric with `pd.to_numeric(..., errors="coerce")`, converting blanks to `NaN`, and the resulting 11 missing values were imputed using the **median** of `TotalCharges` rather than the mean, since the distribution of charges is right-skewed and the median is more robust to that skew for a small number of near-zero-tenure customers.

**String corrections.** Beyond `TotalCharges`, the target column `Churn` was stored as `"Yes"`/`"No"` strings and mapped to a binary integer (`1`/`0`) suitable for `binary_crossentropy` loss. The non-predictive `customerID` column (a unique string identifier per row) was dropped entirely, as it carries no generalizable signal and would only encourage the network to memorize identities rather than learn patterns.

**Categorical indexing choice.** Two different encoding strategies were deliberately applied depending on cardinality:
- **Binary categorical columns** (`gender`, `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`) — each has exactly two categories, so `LabelEncoder` (0/1) was used. This is safe here because binary label encoding does not impose a false ordinal relationship (there are only two states, so "greater than" has no meaning to distort).
- **Multi-class categorical columns** (`MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaymentMethod`) — these have 3+ unrelated categories (e.g., "DSL", "Fiber optic", "No"). Label-encoding these would incorrectly imply an ordinal relationship (e.g., that "Fiber optic" > "DSL" numerically), which would mislead the network's weighted sums. Instead, `pd.get_dummies(..., drop_first=True)` one-hot encoded these columns, expanding the feature space from 19 predictive columns to 30, while dropping the first category per group to avoid multicollinearity (the dummy variable trap).

Finally, the three genuinely continuous numeric columns — `tenure`, `MonthlyCharges`, `TotalCharges` — were standardized using `StandardScaler`, fit **only on the training split** (never the test split) to prevent data leakage, then applied to both. This step matters more for neural networks than for tree-based models: unscaled inputs with wide differing ranges (e.g., tenure in months vs. TotalCharges in the thousands) can cause unstable gradients and slow, uneven convergence during backpropagation.

The final processed feature matrix contained **30 columns** across **7,043 rows**, split 80/20 (5,634 train / 1,409 test) using stratified sampling on `Churn` to preserve the original class ratio in both splits.

---

## 2. ANN Structural Profile

The model is a fully connected feed-forward network built with Keras's `Sequential` API, consisting of:

| Layer | Type | Units | Activation | Parameters |
|---|---|---|---|---|
| Input | — | 30 (features) | — | — |
| Hidden 1 | Dense | 32 | ReLU | 992 |
| Hidden 2 | Dense | 16 | ReLU | 528 |
| Output | Dense | 1 | Sigmoid | 17 |

**Total trainable parameters: 1,537.**

The **input dimensionality (30)** matches the number of processed features exactly after one-hot encoding, ensuring every engineered signal — demographic, service subscription, contract type, and billing behavior — is passed into the network.

The two **hidden layers taper from 32 → 16 units**, a common funnel pattern that progressively compresses the feature representation, forcing the network to learn increasingly abstract combinations of the raw inputs (e.g., combining contract type + tenure + payment method into a latent "churn risk" representation) rather than simply memorizing individual features.

**ReLU activation** was used in both hidden layers because it is computationally cheap, avoids the vanishing-gradient problem common with sigmoid/tanh in deeper stacks, and empirically converges faster for tabular classification tasks of this size.

The **output layer** uses a single neuron with **sigmoid activation**, squashing the final linear combination into a probability between 0 and 1 — appropriate for binary classification, and directly compatible with the `binary_crossentropy` loss function used during compilation.

With only ~1.5K parameters against 5,634 training examples, the model is intentionally lightweight relative to the dataset size — a deliberate choice to keep the architecture simple and interpretable for this assignment, though this capacity trade-off is discussed further in Section 5.

---

## 3. Training & Optimization Tracking

The model was compiled with the **Adam optimizer** (adaptive learning rate, combining momentum and RMSProp-style scaling) and trained for **50 epochs** at a **batch size of 32**, with 20% of the training set (1,127 samples) held out for validation monitoring.

**Loss behavior.** Training loss decreased monotonically and smoothly across all 50 epochs, from an initial ~0.47 down to ~0.357 — indicating stable, well-behaved gradient descent with no divergence or oscillation. Training accuracy rose correspondingly from ~77.7% to ~84.0%.

**Epoch transitions.** The most informative transition occurs around **epoch 5–8**, where **validation loss reaches its minimum** (~0.442–0.443) before beginning a slow, steady climb for the remainder of training, ending at ~0.469 by epoch 50. Validation accuracy tracks a similar pattern: it peaks in the high-70s (~78.3%) in the early-to-mid epochs, then gradually drifts down to ~77.3% by epoch 50, with noisy fluctuation throughout.

**Decoupling analysis (training vs. validation).** From roughly epoch 10 onward, a clear divergence emerges: training loss keeps falling while validation loss rises — the textbook signature of **overfitting**. This means that after the first ~10 epochs, additional training epochs improve the model's fit to the *training* data's idiosyncrasies (including noise specific to those 5,634 rows) without improving — and eventually harming — its ability to generalize to unseen validation data. The gap between the two curves widens steadily but not dramatically (final accuracy gap ≈ 6–7 percentage points, final loss gap ≈ 0.11), indicating **mild, not severe, overfitting** — consistent with a small network (1,537 parameters) trained without regularization on a moderately sized dataset with real, unavoidable label noise. This behavior is expected given the task specification (fixed 50-epoch training, no early stopping or dropout) and is diagnostic rather than indicative of an implementation defect.

---

## 4. Evaluation & Results

On the held-out test set (1,409 samples), the model achieved:

- **Test loss:** 0.4567
- **Test accuracy:** 77.08%

The **classification report** reveals a significant asymmetry between classes:

| Class | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| No Churn | 0.85 | 0.83 | 0.84 | 1,035 |
| Churn | 0.56 | 0.60 | 0.58 | 374 |

**Overall accuracy (77%) is misleading in isolation** given the class imbalance (1,035 vs. 374, ≈73.5%/26.5%). A naive model that always predicts "No Churn" would already score ~73.5% accuracy without learning anything — so the true measure of the model's value lies in the "Churn" class metrics.

The model shows a clear **bias toward predicting the majority class ("No Churn")**: precision and recall for churners (0.56 and 0.60, respectively) are substantially weaker than for non-churners (0.85 and 0.83). In practical terms, this means:
- **~40% of actual churners are missed** (false negatives) — a costly failure mode for a retention use case, since these are exactly the customers a business would want to intervene with.
- **Of customers flagged as "will churn," only 56% actually do** — meaning retention campaigns targeted using this model would waste resources on a substantial share of customers who weren't going to leave anyway.

The confusion matrix visually confirms this: the "No Churn" diagonal cell dominates in volume, while the "Churn" row shows a non-trivial number of false negatives relative to true positives — a direct consequence of the imbalanced training distribution and the model's default (unweighted) loss function, which treats every misclassification equally regardless of class frequency.

---

## 5. Challenges & Engineering Solutions

**Challenge 1 — Class imbalance.** With churners representing only ~26.5% of the dataset, the network's unweighted `binary_crossentropy` loss naturally biases predictions toward the majority class, since correctly classifying the dominant class contributes more to reducing average loss. *Engineering response:* this was diagnosed via the classification report (low recall on the minority class) rather than accuracy alone, which is the correct diagnostic tool for imbalanced problems. A follow-up remedy (not applied here to preserve the assignment's specified architecture) would be to pass `class_weight={0: 1.0, 1: 2.77}` (inverse class frequency) to `model.fit()`, or apply oversampling techniques like SMOTE on the training split only.

**Challenge 2 — String-corrupted numeric column (`TotalCharges`).** The presence of blank strings silently masked what would otherwise be a numeric column, and a naive `.isnull().sum()` check before type coercion would have wrongly reported zero missing values. *Engineering response:* explicit type coercion (`pd.to_numeric(errors="coerce")`) followed by targeted median imputation, cross-verified against the fact that all blanks corresponded to `tenure == 0`, confirming the missingness was structural and not a data quality defect requiring row deletion.

**Challenge 3 — Overfitting emerging mid-training.** As detailed in Section 3, validation loss begins rising after epoch ~8, while the assignment specification fixed training at exactly 50 epochs with no early stopping. *Engineering response:* rather than silently accepting a possibly sub-optimal final-epoch model, the divergence was explicitly tracked and visualized (Part 7 plots) so that the phenomenon is documented and understood, even though the fixed-epoch constraint was respected as specified.

**Challenge 4 — Data leakage risk during scaling.** A common implementation mistake is to fit `StandardScaler` on the full dataset before splitting, which leaks test-set statistics (mean/variance) into the training pipeline. *Engineering response:* the scaler was deliberately fit only on `X_train`, with `X_test` transformed using the training-derived parameters, preserving a clean train/test boundary.

---

## 6. Strategic Conclusion

The ANN successfully learns a meaningful churn signal, outperforming a naive majority-class baseline on the minority class specifically (56% precision / 60% recall on churners, versus 0% for a trivial baseline), while achieving strong performance on the majority class (85%/83%). However, the model's practical utility for a retention campaign is currently limited by its moderate recall on churners and the mild overfitting visible after epoch ~8.

**Recommended future enhancements:**

1. **Class-weighted or resampled training** — applying `class_weight` in `model.fit()` or SMOTE-based oversampling on the training set would directly counteract the model's bias toward the majority class, likely improving churn recall at some cost to churn precision (a trade-off that should be tuned against the business cost of false negatives vs. false positives).
2. **Regularization to curb overfitting** — introducing `Dropout(0.2–0.3)` between hidden layers, L2 weight regularization, or `EarlyStopping(monitor="val_loss", patience=5–10)` would allow training to halt near the true validation-loss minimum (~epoch 8) rather than continuing to epoch 50 by fixed schedule.
3. **Testing heavier/deeper architectures** — a wider first layer (e.g., 64 units) or an additional hidden layer might capture more complex feature interactions, though this should be evaluated against the added overfitting risk given the dataset's modest size (~5,600 training rows).
4. **Alternative optimizers and learning-rate schedules** — experimenting with `AdamW` (decoupled weight decay) or a `ReduceLROnPlateau` callback tied to `val_loss` could smooth the late-training divergence observed here.
5. **Threshold tuning** — since the default 0.5 decision threshold favors the majority class, adjusting the classification threshold downward (e.g., to 0.35–0.4) based on the ROC or precision-recall curve could improve churner recall without retraining the model at all — a low-cost, high-leverage next step.

Taken together, these findings demonstrate that while the current fixed-specification ANN is a solid baseline, targeted engineering interventions around class imbalance and regularization represent the clearest path to a production-ready churn model.
