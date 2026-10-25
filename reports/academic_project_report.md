# Academic Project Report: Bank Marketing Subscription Prediction System Using Machine Learning

---

## 1. Title Page
- **Project Title:** Bank Marketing Subscription Prediction System Using Machine Learning
- **Application Domain:** Banking, FinTech, and Predictive Customer Analytics
- **System Name:** BankerEye ML Platform
- **Target Audience:** Engineering College Academic Evaluation, Machine Learning Practitioners, Financial Marketing Analysts
- **Version:** 1.0.0
- **Academic Year:** 2024–2025

---

## 2. Abstract
Direct telemarketing campaigns conducted by commercial banking institutions to promote term deposit products typically suffer from low conversion rates (historically ~10% to 15%) and substantial operational expenditures. This project designs, implements, benchmarks, and deploys an end-to-end Machine Learning prediction system named **BankerEye**. 

The system leverages the benchmark UCI Bank Marketing dataset comprising 45,211 observational campaign records. To adhere strictly to real-world deployment constraints and prevent target leakage, the feature `duration` (call duration in seconds) is intentionally excluded from the primary model pipeline. Four core supervised machine learning algorithms are trained and evaluated under an identical, stratified 80/20 train/test partition: **Logistic Regression**, **Decision Tree Classifier**, **K-Nearest Neighbours (KNN)**, and **Random Forest Classifier**.

Each model is regularized, hyperparameter-tuned via 5-fold cross-validated grid search on the training split, and calibrated via 3-fold cross-validated isotonic regression. On the held-out test partition of 9,043 instances, the **Random Forest Classifier** achieved the highest overall discriminative performance with an ROC-AUC of **79.86%** (Accuracy: 86.97%, F1-Score: 47.32%), while the **Decision Tree Classifier** attained an F1-Score of **47.51%** (Accuracy: 88.00%, Recall: 46.41%). Non-parametric percentile bootstrap evaluation (n=500) demonstrates that the 95% confidence intervals for Decision Tree F1 [0.4468, 0.5011] and Random Forest F1 [0.4464, 0.4965] overlap, establishing that their predictive performances are not statistically distinguishable on this test set. The system features a modular Python architecture consisting of a **Flask REST API** backend and a high-performance **Streamlit** analytical dashboard supporting interactive single-customer propensity scoring, bulk CSV batch predictions, dynamic Plotly visualizations, and automated academic PDF report generation.

---

## 3. Introduction
Retail banks rely heavily on retail deposits as a primary source of low-cost capital for lending activities. Fixed-term deposits guarantee the institution a locked capital pool for a specified maturity horizon. However, executing unsegmented mass outbound phone calls incurs high telecommunication toll charges, call center labor costs, and customer relationship friction.

Machine learning offers the capability to analyze historical customer demographics, financial standings, and prior marketing interactions to identify customer cohorts with a statistically elevated likelihood of subscribing. By ranking customer leads prior to outbound calling, marketing teams can concentrate outreach on high-propensity prospects, improving campaign return on investment (ROI).

---

## 4. Problem Statement
Given a set of pre-contact customer demographic features (age, job, marital status, education), financial obligations (credit default, average yearly balance, housing loan, personal loan), and historical campaign interactions (contact method, timing, previous campaign outcomes), develop a binary classification model that accurately predicts the target variable:
$$y \in \{0, 1\}$$
where $0$ indicates "No (Will Not Subscribe)" and $1$ indicates "Yes (Will Subscribe)".

### Critical Feature Leakage Constraint
The UCI Bank Marketing dataset contains the attribute `duration` (the elapsed duration of the phone call in seconds). While call duration is strongly correlated with conversion success, it is strictly unknown prior to placing the phone call. Incorporating call duration into a prospective customer lead-scoring model represents severe target leakage, yielding artificially inflated metrics that fail in real-world telemarketing operations. Therefore, this project mandates the complete exclusion of `duration` from the primary prediction model.

---

## 5. Objectives
1. **Pipeline Engineering:** Build a robust, reproducible data preprocessing pipeline with automatic delimiter detection, missing-value validation, engineered `never_contacted` indicators, and stratified train/test partitioning.
2. **Leakage Prevention:** Rigorously eliminate call duration from feature matrices.
3. **Multi-Model Benchmark:** Train, tune, and compare four diverse supervised classification algorithms on an identical held-out test set.
4. **Isotonic Calibration:** Wrap models in 3-fold cross-validated isotonic regression to deliver calibrated posterior probabilities and minimize Brier score.
5. **Statistical Significance Testing:** Generate 500-sample bootstrap 95% confidence intervals for F1 and ROC-AUC to prevent overconfident claims of superiority.
6. **Full-Stack Deployment:** Develop a decoupled Flask REST API backend paired with an interactive Streamlit analytics frontend.
7. **Dual Inference:** Support both interactive single-customer profiling and high-throughput CSV batch predictions.
8. **Automated Reporting:** Deliver downloadable evaluation summaries (JSON), metrics comparisons (CSV), and formal academic PDF reports.

---

## 6. Scope of the Project
- **In Scope:** Supervised tabular classification using Scikit-Learn; feature encoding via `ColumnTransformer`; class imbalance handling via balanced weighting; probability calibration via `CalibratedClassifierCV`; threshold optimization; REST API endpoints for training, evaluation, single and batch prediction; interactive Streamlit web dashboard.
- **Out of Scope:** Voice recording analysis, real-time telephony streaming, automated autodialers, and unconstrained LLM text generation.

---

## 7. Literature Review — Minimum Five Research Papers
The table below summarizes research papers (2021–2024) investigating machine learning on the UCI Bank Marketing dataset, audited for citation verification:

| # | Paper Title | Authors & Year | Venue & DOI | Verification Status | Core Algorithms | Reported Findings & Relevance |
|---|---|---|---|---|---|---|
| 1 | Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics | N. Alessa et al. (2023) | IEEE ICCMA<br>DOI: 10.1109/ICCMA59762.2023.10374595 | Unverified, check before citing | LR, DT, KNN, RF, SVM + PySpark | Random Forest ensemble outperformed individual linear models across customer sub-cohorts. Directly validates our 4-model selection. |
| 2 | Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning | D. P. Singh et al. (2024) | IEEE TIACOMP<br>DOI: 10.1109/TIACOMP64125.2024.00085 | Unverified, check before citing | RF, DT, LR + SMOTE | Mitigating class imbalance improved subscription recall from ~30% to >70%, avoiding majority class dominance. Confirms our class-weighting design. |
| 3 | Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies | A. K. Dixit & R. Kokila (2024) | IEEE ICONAT<br>IEEE Doc: 10700543 | Unverified, check before citing | KNN, LR, NB, DT, RF, XGBoost | Normalization and ensemble stacking reached high accuracy. Confirms the necessity of `StandardScaler` for continuous attributes. |
| 4 | Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns | M. F. Tanvir et al. (2024) | IEEE DASA / arXiv<br>DOI: 10.48550/arXiv.2410.21539 | Verified | Bayesian Logit, Probit, Logit | Calibrated probabilistic outputs prevent binary cutoff errors, justifying continuous probability scores and risk gauge charts. |
| 5 | A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models | M. Z. Khan et al. (2021) | Springer LNCS (vol. 12956)<br>DOI: 10.1007/978-3-030-87010-9_8 | Unverified, check before citing | RF, DT, LR, SHAP | Balance and previous campaign history are primary predictors; explainable attribution is mandatory for banking compliance. |

---

## 8. Existing System vs. Proposed System

### Existing Telemarketing Approaches
- **Manual Outbound Cold Calling:** Telemarketers call customer lists sorted arbitrarily or chronologically.
- **Rule-Based Filtering:** Naive heuristics that fail to capture non-linear feature interactions.
- **High Wastage:** ~88% of calls are placed to disinterested customers, burning call center hours and generating customer friction.

### Proposed BankerEye System
- **Machine Learning Propensity Scoring:** Customers ranked by calibrated algorithmic subscription probability.
- **Leakage-Free Feature Processing:** Focuses purely on verifiable pre-call customer attributes.
- **Balanced Class Weighting:** Counteracts the 88/12 class imbalance to prioritize recall for actual depositors.
- **Calibrated Posterior Probabilities:** Minimizes Brier scores through 3-fold cross-validated isotonic regression.
- **Validation-Tuned Decision Thresholds:** Maximizes operational F1 rather than defaulting to arbitrary 0.5 cutoffs.

---

## 9. System Architecture
```
+-------------------------------------------------------------------------+
|                          Streamlit Frontend                             |
|  [Dashboard] [Dataset Explorer] [Model Comparison] [Predictor] [Batch]   |
+------------------------------------+------------------------------------+
                                     | JSON REST HTTP (Requests)
                                     v
+-------------------------------------------------------------------------+
|                          Flask REST API Backend                         |
|   /api/health | /api/dataset/* | /api/models/* | /api/predict | /reports |
+------------------------------------+------------------------------------+
                                     |
         +---------------------------+---------------------------+
         |                                                       |
         v                                                       v
+---------------------------------+     +---------------------------------+
|      Preprocessing Service      |     |     Model Training Service      |
| - Delimiter Detection           |     | - Stratified 5-Fold GridSearch  |
| - PdaysFeatureEngineer          |     | - Isotonic Calibration (CV=3)   |
| - ColumnTransformer Pipeline    |     | - Optimal Threshold Tuning      |
| - Duration Exclusion Guard      |     | - 500-Iteration Bootstrap CIs   |
+---------------------------------+     +---------------------------------+
```

---

## 10. Dataset and Preprocessing Pipeline
- **Benchmark Source:** UCI Machine Learning Repository — Bank Marketing Dataset ([Moro et al., 2014](https://archive.ics.uci.edu/dataset/222/bank+marketing)).
- **Observations:** 45,211 observational campaign calls from a Portuguese retail bank.
- **Target Distribution:** 39,922 'no' (88.30%) and 5,289 'yes' (11.70%).
- **Categorical Handling:** One-hot encoded via `OneHotEncoder(handle_unknown="ignore")`.
- **Numerical Scaling:** Standardized via `StandardScaler`.
- **Feature Engineering:** `PdaysFeatureEngineer` detects `pdays == -1` to generate a binary `never_contacted` flag and sets `pdays = 0` within the Scikit-learn pipeline, preserving inference consistency.

---

## 11. Methodology and Algorithm Descriptions

### Model 1: Logistic Regression
- **Mathematical Basis:** Models log-odds as a linear combination of predictors:
  $$P(y=1|X) = \frac{1}{1 + e^{-(\beta_0 + \sum \beta_i X_i)}}$$
- **Hyperparameters:** `solver='lbfgs'`, `max_iter=1000`, `C=1.0`, `class_weight='balanced'`, `random_state=42`.
- **Calibration:** `CalibratedClassifierCV(method='isotonic', cv=3)`.
- **Optimal Threshold:** 0.25 (tuned to maximize F1).

### Model 2: Decision Tree Classifier
- **Mathematical Basis:** Partitions feature space using recursive binary splitting to minimize Gini Impurity:
  $$I_G(p) = 1 - \sum_{i=1}^C p_i^2$$
- **Hyperparameters:** `max_depth=10`, `min_samples_split=20`, `class_weight='balanced'`, `random_state=42`.
- **Calibration:** `CalibratedClassifierCV(method='isotonic', cv=3)`.
- **Optimal Threshold:** 0.22 (tuned to maximize F1).

### Model 3: K-Nearest Neighbours (KNN)
- **Mathematical Basis:** Non-parametric instance-based voting among nearest neighbors in standardized Euclidean space:
  $$d(x, x') = \sqrt{\sum_{i=1}^p (x_i - x'_i)^2}$$
- **Hyperparameters:** `n_neighbors=5`, `metric='minkowski'`, `p=2`. (Note: KNN does not support `class_weight`).
- **Calibration:** `CalibratedClassifierCV(method='isotonic', cv=3)`.
- **Optimal Threshold:** 0.17 (tuned to maximize F1).

### Model 4: Random Forest Classifier
- **Mathematical Basis:** Bagging ensemble of $B=100$ decorrelated decision trees with random feature sub-sampling:
  $$\hat{y} = \text{mode} \{ T_1(X), T_2(X), \dots, T_B(X) \}$$
- **Hyperparameters:** `n_estimators=100`, `max_depth=12`, `class_weight='balanced'`, `random_state=42`.
- **Calibration:** `CalibratedClassifierCV(method='isotonic', cv=3)`.
- **Optimal Threshold:** 0.22 (tuned to maximize F1).

---

## 12. Train/Test Split and Experimental Setup
- **Dataset Partitioning:** 80% Training ($N_{train} = 36,168$), 20% Held-Out Testing ($N_{test} = 9,043$).
- **Stratification:** Maintained identical positive target ratio (11.70%) across both partitions.
- **Hardware/Software Environment:** Windows x64, Python 3.11.9, Scikit-Learn 1.9.0, Pandas 2.2.3, Flask 3.0.3, Streamlit 1.66.1.
- **Evaluation Criteria:** All four models scored on the exact same held-out test data. No test data utilized in model fitting or preprocessing parameter selection.

---

## 13. Experimental Results: Empirical Four-Model Benchmark
All results measured on the held-out test split of 9,043 instances (excluding `duration`):

| Algorithm | Accuracy | Precision (yes) | Recall (yes) | F1-Score (yes) | 95% Bootstrap CI (F1) | ROC-AUC | 95% CI (ROC-AUC) | Brier Score |
|---|---|---|---|---|---|---|---|---|
| **Random Forest Classifier** | 86.97% | 44.91% | 50.00% | 47.32% | [0.4464, 0.4965] | **79.86%** | [0.7841, 0.8138] | **0.0822** |
| **Decision Tree Classifier** | **88.00%** | **48.66%** | 46.41% | **47.51%** | [0.4468, 0.5011] | 77.76% | [0.7611, 0.7947] | 0.0834 |
| **Logistic Regression** | 87.84% | 47.76% | 42.34% | 44.89% | [0.4217, 0.4732] | 77.20% | [0.7578, 0.7889] | 0.0850 |
| **K-Nearest Neighbours (KNN)**| 86.42% | 41.13% | 37.24% | 39.09% | [0.3649, 0.4179] | 72.33% | [0.7056, 0.7416] | 0.0897 |

---

## 14. Figures and Confusion Matrices
On the held-out test split of 9,043 instances (7,985 actual non-subscribers, 1,058 actual subscribers):

### Random Forest Classifier
- **True Negatives (TN):** 7,336 | **False Positives (FP):** 649
- **False Negatives (FN):** 529 | **True Positives (TP):** 529

### Decision Tree Classifier
- **True Negatives (TN):** 7,467 | **False Positives (FP):** 518
- **False Negatives (FN):** 567 | **True Positives (TP):** 491

### Logistic Regression
- **True Negatives (TN):** 7,495 | **False Positives (FP):** 490
- **False Negatives (FN):** 610 | **True Positives (TP):** 448

### K-Nearest Neighbours (KNN)
- **True Negatives (TN):** 7,421 | **False Positives (FP):** 564
- **False Negatives (FN):** 664 | **True Positives (TP):** 394

---

## 15. Results and Discussion
1. **Statistical Distinguishability:** The 95% bootstrap confidence intervals for Decision Tree [0.4468, 0.5011] and Random Forest [0.4464, 0.4965] overlap. Consequently, their performances are **not statistically distinguishable** on this held-out test set.
2. **Discriminative Capability:** **Random Forest** achieved the highest ROC-AUC (**79.86%**), demonstrating strong ranking capability across classification thresholds.
3. **Calibrated Probability Alignment:** By applying 3-fold cross-validated isotonic calibration, all four algorithms achieved Brier scores under 0.090, confirming that output probability estimates reflect genuine empirical conversion frequencies.
4. **Telemarketing Campaign Trade-Off:** In retail banking, false positives cost modest telephone toll charges, while false negatives cost valuable long-term deposit capital. Decision Tree and Random Forest provide the ideal operational balance for outbound outreach teams.

---

## 16. Limitations & Ethical Considerations
- **Non-Causal Association:** Machine learning feature importance rankings reflect statistical correlation within historical observations. They must not be construed as definitive causal mechanisms.
- **Fair Lending Compliance:** Customer demographic features (age, marital status, job) must be audited to ensure algorithms do not perpetuate discriminatory lending practices prohibited under fair lending laws.
- **Model Role:** BankerEye is strictly an operational decision-support tool designed to sequence outreach lists. It does not possess authority to autonomously deny banking services.

---

## 17. References
1. S. Moro, P. Cortez, and P. Rita, "A data-driven approach to predict the success of bank telemarketing," *Decision Support Systems*, vol. 62, pp. 22–31, 2014. [DOI: 10.1016/j.dss.2014.03.001]
2. N. Alessa et al., "Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics," *2023 11th International Conference on Control, Mechatronics and Automation (ICCMA)*, pp. 1–6, 2023. [DOI: 10.1109/ICCMA59762.2023.10374595] *(Unverified)*
3. D. P. Singh et al., "Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning," *2024 Trends in Information and Advanced Computing (TIACOMP)*, pp. 1–6, 2024. [DOI: 10.1109/TIACOMP64125.2024.00085] *(Unverified)*
4. A. K. Dixit and R. Kokila, "Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies," *2024 3rd International Conference for Advancement in Technology (ICONAT)*, IEEE Doc: 10700543, 2024. *(Unverified)*
5. M. F. Tanvir, M. M. Hossain, and M. A. Jishan, "Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns," *International Conference on Decision Aid Sciences and Applications (DASA)*, arXiv:2410.21539, 2024. [DOI: 10.48550/arXiv.2410.21539] *(Verified)*
6. M. Z. Khan, S. Munquad, and T. S. M. Rao, "A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models," *Computational Science and Its Applications — ICCSA 2021*, LNCS vol. 12956, Springer, pp. 93–103, 2021. [DOI: 10.1007/978-3-030-87010-9_8] *(Unverified)*
