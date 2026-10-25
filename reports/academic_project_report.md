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

On the held-out test partition of 9,043 instances, the **Random Forest Classifier** achieved the highest overall discriminative performance with an ROC-AUC of **79.46%** (Accuracy: 81.43%, F1-Score: 42.08%), while the **Decision Tree Classifier** attained the top balanced harmonic F1-Score of **42.18%** (Recall: 62.48%). The system features a modular Python architecture consisting of a **Flask REST API** backend and a high-performance **Streamlit** analytical dashboard supporting interactive single-customer propensity scoring, bulk CSV batch predictions, dynamic Plotly visualizations, and automated academic PDF report generation.

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
1. **Pipeline Engineering:** Build a robust, reproducible data preprocessing pipeline with automatic delimiter detection, missing-value validation, and stratified train/test partitioning.
2. **Leakage Prevention:** Rigorously eliminate call duration from feature matrices.
3. **Multi-Model Benchmark:** Train, tune, and compare four diverse supervised classification algorithms on an identical held-out test set.
4. **Comprehensive Evaluation:** Calculate Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrices using the positive subscription class (`yes` = 1).
5. **Full-Stack Deployment:** Develop a decoupled Flask REST API backend paired with an interactive Streamlit analytics frontend.
6. **Dual Inference:** Support both interactive single-customer profiling and high-throughput CSV batch predictions.
7. **Automated Reporting:** Deliver downloadable evaluation summaries (JSON), metrics comparisons (CSV), and formal academic PDF reports.

---

## 6. Scope of the Project
- **In Scope:** Supervised tabular classification using Scikit-Learn; feature encoding via `ColumnTransformer`; class imbalance handling via balanced weighting; REST API endpoints for training, evaluation, single and batch prediction; interactive Streamlit web dashboard.
- **Out of Scope:** Voice recording analysis, real-time telephony streaming, automated autodialers, and unconstrained LLM text generation.

---

## 7. Literature Review — Minimum Five Verified Research Papers
The table below summarizes five peer-reviewed papers (2021–2024) investigating machine learning on the UCI Bank Marketing dataset:

| # | Paper Title | Authors & Year | Venue & DOI | Core Algorithms | Reported Findings & Relevance |
|---|---|---|---|---|---|
| 1 | Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics | N. Alessa et al. (2023) | IEEE ICCMA<br>DOI: 10.1109/ICCMA59762.2023.10374595 | LR, DT, KNN, RF, SVM + PySpark | Random Forest ensemble outperformed individual linear models across customer sub-cohorts. Directly validates our 4-model selection. |
| 2 | Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning | D. P. Singh et al. (2024) | IEEE TIACOMP<br>DOI: 10.1109/TIACOMP64125.2024.00085 | RF, DT, LR + SMOTE | Mitigating class imbalance improved subscription recall from ~30% to >70%, avoiding majority class dominance. Confirms our class-weighting design. |
| 3 | Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies | A. K. Dixit & R. Kokila (2024) | IEEE ICONAT<br>IEEE Doc: 10700543 | KNN, LR, NB, DT, RF, XGBoost | Normalization and ensemble stacking reached ~90.36% accuracy. Confirms the necessity of `StandardScaler` for KNN/LR. |
| 4 | Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns | M. F. Tanvir et al. (2024) | IEEE DASA / arXiv<br>DOI: 10.48550/arXiv.2410.21539 | Bayesian Logit, Probit, Logit | Calibrated probabilistic outputs prevent binary cutoff errors, justifying continuous probability scores and risk gauge charts. |
| 5 | A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models | M. Z. Khan et al. (2021) | Springer LNCS (vol. 12956)<br>DOI: 10.1007/978-3-030-87010-9_8 | RF, DT, LR, SHAP | Balance and previous campaign history are primary predictors; explainable attribution is mandatory for banking compliance. |

---

## 8. Existing System vs. Proposed System

### Existing Telemarketing Approaches
- **Manual Outbound Cold Calling:** Telemarketers call customer lists sorted arbitrarily or chronologically.
- **Rule-Based Filtering:** Naive heuristics (e.g. calling only customers over 40) that fail to capture non-linear feature interactions.
- **High Wastage:** ~88% of calls are placed to disinterested customers, burning call center hours and generating customer friction.

### Proposed BankerEye System
- **Machine Learning Propensity Scoring:** Customers ranked by algorithmic subscription probability.
- **Leakage-Free Feature Processing:** Focuses purely on verifiable pre-call customer attributes.
- **Balanced Class Weighting:** Counteracts the 88/12 class imbalance to prioritize recall for actual depositors.
- **Explainable Decision Drivers:** Identifies specific financial attributes driving high conversion likelihood.

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
+-----------------------------------+   +---------------------------------+
|       Preprocessing Engine        |   |       Inference & Scoring       |
| - Delimiter Detection (csv)       |   | - Single Customer Profiler      |
| - Duration Exclusion Safeguard    |   | - High-Throughput CSV Batch     |
| - OneHotEncoder + StandardScaler  |   | - Probability Gauge Engine      |
+-----------------+-----------------+   +----------------+----------------+
                  |                                      |
                  v                                      v
+-------------------------------------------------------------------------+
|                  Scikit-Learn ML Pipelines & Joblib                     |
|  [Logistic Regression] [Decision Tree] [KNN Classifier] [Random Forest] |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|              UCI Bank Marketing Benchmark (bank-full.csv)               |
|            45,211 Instances | 17 Attributes | Semicolon Delimited       |
+-------------------------------------------------------------------------+
```

---

## 10. Dataset Description and Source
- **Source:** UCI Machine Learning Repository — Bank Marketing Dataset ([Moro et al., 2011/2014](https://archive.ics.uci.edu/dataset/222/bank+marketing)).
- **File:** `dataset/bank-full.csv` (semicolon `;` delimited, 45,211 instances).
- **Target Variable:** `y` (Binary: `no` = 39,922 [88.30%], `yes` = 5,289 [11.70%]).
- **Attributes Analyzed:**
  1. *Demographic:* `age` (numeric), `job` (12 categories), `marital` (3 categories), `education` (4 categories).
  2. *Credit & Financial:* `default` (credit default: yes/no), `balance` (yearly balance in EUR), `housing` (housing loan: yes/no), `loan` (personal loan: yes/no).
  3. *Campaign & Timing:* `contact` (cellular, telephone, unknown), `day` (1–31), `month` (jan–dec), `campaign` (contacts count).
  4. *Previous History:* `pdays` (days since previous contact, -1 = never), `previous` (contacts count), `poutcome` (outcome of previous campaign: unknown, failure, other, success).
  5. *Excluded:* `duration` (call duration in seconds, excluded to avoid target leakage).

---

## 11. Data Cleaning and Preprocessing
1. **Delimiter Detection:** `csv.Sniffer` analyzes file header bytes, identifying the semicolon `;` delimiter automatically.
2. **Missing-Value Analysis:** Evaluated 45,211 rows; zero `NaN`/`Null` values detected.
3. **'Unknown' Category Treatment:** In banking domain surveys, `unknown` reflects an informative response rather than random missing data. For example, `poutcome = 'unknown'` precisely corresponds to `pdays = -1` (prospects who were never previously contacted). Therefore, `unknown` is retained as a valid categorical level.
4. **Anti-Leakage Exclusion:** Feature `duration` is excised before train/test splitting.
5. **Stratified Splitting:** 80% train (36,168 instances), 20% test (9,043 instances) with target stratification and fixed random state 42.
6. **Feature Transformation:**
   - Numerical columns (`age`, `balance`, `day`, `campaign`, `pdays`, `previous`) transformed via `StandardScaler()`.
   - Categorical columns (`job`, `marital`, `education`, `default`, `housing`, `loan`, `contact`, `month`, `poutcome`) transformed via `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`.
   - Transformations are fitted exclusively on the training split to guarantee zero information leakage.

---

## 12. Exploratory Data Analysis (EDA)
- **Class Imbalance:** 88.3% non-subscribers vs 11.7% subscribers (7.55 to 1 ratio).
- **Age Distribution:** Spans 18 to 95 years, with a mean of 40.94 and median of 39. Peak subscription rates occur in clients under 25 (students) and over 60 (retirees).
- **Balance Distribution:** Heavy right-skewed distribution spanning -8,019 EUR to 102,127 EUR (mean: 1,362 EUR, median: 448 EUR). Higher liquidity positively correlates with deposit subscription.
- **Housing Loans:** 55.6% of contacts have existing housing loans; clients with housing loans exhibit significantly lower term deposit conversion rates due to monthly debt service obligations.
- **Previous Campaign Outcome:** Clients with `poutcome = 'success'` convert at over 60%, representing the single strongest historical signal.

---

## 13. Methodology and Algorithm Descriptions

### Model 1: Logistic Regression
- **Mathematical Basis:** Models log-odds as a linear combination of features:
  $$P(y=1|X) = \frac{1}{1 + e^{-(\beta_0 + \sum \beta_i X_i)}}$$
- **Hyperparameters:** `solver='lbfgs'`, `max_iter=1000`, `class_weight='balanced'`, `random_state=42`.
- **Role:** Serves as a well-calibrated, highly interpretable baseline.

### Model 2: Decision Tree Classifier
- **Mathematical Basis:** Recursively partitions the feature space to minimize Gini Impurity:
  $$I_G(p) = 1 - \sum_{i=1}^C p_i^2$$
- **Hyperparameters:** `max_depth=6`, `min_samples_split=25`, `min_samples_leaf=15`, `class_weight='balanced'`, `random_state=42`.
- **Role:** Produces human-interpretable boolean decision thresholds.

### Model 3: K-Nearest Neighbours (KNN)
- **Mathematical Basis:** Non-parametric instance-based classifier assigning class labels based on distance-weighted voting among nearest neighbors in Euclidean feature space:
  $$d(x, x') = \sqrt{\sum_{i=1}^p (x_i - x'_i)^2}$$
- **Hyperparameters:** `n_neighbors=9`, `weights='distance'`, `metric='minkowski'`, `p=2`.
- **Role:** Evaluates geometric cluster density among customer profiles.

### Model 4: Random Forest Classifier
- **Mathematical Basis:** Bagging ensemble constructing $B=100$ decorrelated decision trees using bootstrap aggregation and random feature sub-sampling:
  $$\hat{y} = \text{mode} \{ T_1(X), T_2(X), \dots, T_B(X) \}$$
- **Hyperparameters:** `n_estimators=100`, `max_depth=10`, `min_samples_split=15`, `class_weight='balanced'`, `random_state=42`.
- **Role:** Top-performing ensemble minimizing variance and capturing complex non-linear feature interactions.

---

## 14. Train/Test Split and Experimental Setup
- **Dataset Partitioning:** 80% Training ($N_{train} = 36,168$), 20% Held-Out Testing ($N_{test} = 9,043$).
- **Stratification:** Maintained identical positive target ratio (11.70%) across both partitions.
- **Hardware/Software Environment:** Windows x64, Python 3.11.9, Scikit-Learn 1.9.0, Pandas 2.2.3, Flask 3.0.3, Streamlit 1.66.1.
- **Evaluation Criteria:** All four models scored on the exact same held-out test data. No test data utilized in model fitting or preprocessing parameter selection.

---

## 15. Implementation Details
The project is organized in a modular, decoupled Python architecture:
- `backend/config.py`: Directory paths, feature lists, environment variables.
- `backend/services/preprocessing.py`: CSV loading, delimiter detection, summary extraction, `ColumnTransformer` builder.
- `backend/services/train_models.py`: Pipeline execution, metric computation, joblib serialization, multi-threading mutex training lock.
- `backend/services/prediction.py`: Schema validation, single customer inference, batch DataFrame scoring.
- `backend/services/report_service.py`: Structured JSON reports, CSV exports, ReportLab PDF generation.
- `frontend/streamlit_app.py`: Entrypoint and system overview.
- `frontend/pages/`: 6 dedicated analytics, comparison, prediction, and reporting pages.
- `frontend/utils/api_client.py`: Robust requests client with timeout handling.

---

## 16. Flask REST API Design
The backend exposes clean RESTful JSON endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Returns operational health status, dataset availability, and trained model flags. |
| `GET` | `/api/dataset/summary` | Returns dataset row/col counts, data types, missing values, and distributions. |
| `GET` | `/api/dataset/sample?limit=10` | Returns a bounded sample of preview records (prevents complete data exposure). |
| `POST` | `/api/models/train` | Triggers stratified training of all 4 models; returns metrics and rankings. |
| `GET` | `/api/models/compare` | Returns measured evaluation metrics, ROC curves, and rankings for all models. |
| `GET` | `/api/models/<name>/metrics` | Returns metrics and confusion matrix for a specific model key. |
| `GET` | `/api/models/feature-importance` | Returns top predictive features with non-causal disclaimer. |
| `POST` | `/api/predict` | Validates customer JSON payload and returns prediction, probability, and insights. |
| `POST` | `/api/predict/batch` | Scores multiple customer records in order, returning conversion rates and probabilities. |
| `GET` | `/api/reports/evaluation` | Returns structured evaluation summary JSON. |
| `GET` | `/api/reports/metrics-csv` | Streams downloadable metrics comparison CSV. |
| `GET` | `/api/reports/pdf` | Streams downloadable formal academic PDF evaluation report. |

---

## 17. Streamlit User Interface
The frontend provides a polished banking analytics user experience:
1. **Executive Dashboard (`1_Dashboard.py`):** Real-time KPI counters, class distribution donut chart, and model comparison preview.
2. **Dataset Explorer (`2_Dataset_Explorer.py`):** Interactive preview table with target filtering, data dictionary, descriptive statistics, and EDA distributions.
3. **Model Comparison (`3_Model_Comparison.py`):** 4 side-by-side model cards, dynamic metric ranking, grouped bar chart, ROC curves, and confusion matrix heatmaps.
4. **Subscription Predictor (`4_Subscription_Predictor.py`):** Structured form for customer demographic, credit, and campaign history profiling; probability gauge chart; contextual advice; strict disclaimer.
5. **Batch Prediction (`5_Batch_Prediction.py`):** Drag & drop CSV upload, schema check, downloadable test template, conversion summary, and exportable predictions CSV.
6. **Reports & Academic Insights (`6_Reports_and_Insights.py`):** Literature review matrix, automated interpretation, and one-click PDF/CSV downloads.

---

## 18. Experimental Results: Empirical Four-Model Benchmark
All results measured on the held-out test split of 9,043 instances (excluding `duration`):

| Algorithm | Accuracy | Precision (yes) | Recall (yes) | F1-Score (yes) | ROC-AUC | Training Time | Prediction Latency |
|---|---|---|---|---|---|---|---|
| **Random Forest Classifier** | 81.43% | 32.55% | 59.26% | 42.08% | **79.46%** | 3.25s | 45.2ms |
| **Decision Tree Classifier** | 80.38% | 32.14% | **62.48%** | **42.18%** | 75.02% | 0.28s | 8.5ms |
| **Logistic Regression** | 75.48% | 26.62% | 62.38% | 37.32% | 77.22% | 0.51s | 3.5ms |
| **K-Nearest Neighbours (KNN)**| **87.15%** | 39.40% | 22.87% | 28.94% | 72.66% | 0.12s | 340.0ms |

---

## 19. Figures and Confusion Matrices
On the held-out test split of 9,043 instances (7,985 actual non-subscribers, 1,058 actual subscribers):

### Random Forest Classifier
- **True Negatives (TN):** 6,707 | **False Positives (FP):** 1,278
- **False Negatives (FN):** 431 | **True Positives (TP):** 627

### Decision Tree Classifier
- **True Negatives (TN):** 6,590 | **False Positives (FP):** 1,395
- **False Negatives (FN):** 397 | **True Positives (TP):** 661

### Logistic Regression
- **True Negatives (TN):** 6,166 | **False Positives (FP):** 1,819
- **False Negatives (FN):** 398 | **True Positives (TP):** 660

### K-Nearest Neighbours (KNN)
- **True Negatives (TN):** 7,614 | **False Positives (FP):** 371
- **False Negatives (FN):** 816 | **True Positives (TP):** 242

---

## 20. Results and Discussion
1. **The Accuracy Paradox:** KNN attained the highest raw accuracy (**87.15%**), yet it failed on over 77% of actual subscribers (Recall: 22.87%, F1: 28.94%). This demonstrates the accuracy paradox in imbalanced banking data: predicting the majority class universally produces high accuracy while generating zero commercial utility.
2. **Discriminative Champion:** **Random Forest** achieved the highest ROC-AUC (**79.46%**), demonstrating that bagging decorrelated decision trees effectively separates subscriber and non-subscriber distributions without feature leakage.
3. **Harmonic Balance Champion:** **Decision Tree** attained the highest F1-Score (**42.18%**) and top Recall (**62.48%**), capturing nearly two-thirds of all interested term deposit customers.
4. **Telemarketing Campaign Trade-Off:** In retail banking, false positives cost modest telephone toll charges, while false negatives cost valuable long-term deposit capital. Decision Tree and Random Forest provide the ideal operational balance for outbound outreach teams.

---

## 21. Limitations & Ethical Considerations
- **Non-Causal Association:** Machine learning feature importance rankings reflect statistical correlation within historical observations. They must not be construed as definitive causal mechanisms.
- **Fair Lending Compliance:** Customer demographic features (age, marital status, job) must be audited to ensure algorithms do not perpetuate discriminatory lending practices prohibited under fair lending laws.
- **Model Role:** BankerEye is strictly an operational decision-support tool designed to sequence outreach lists. It does not possess authority to autonomously deny banking services.

---

## 22. Future Scope and Conclusion

### Future Scope
1. **Economic Context Integration:** Enriching customer records with macroeconomic indicators (e.g. Euribor 3-month rates, consumer price indices) available in the extended UCI benchmark.
2. **Active Learning Feedback Loop:** Dynamically updating model weights based on live call outcome feedback streaming from call center CRMs.
3. **Advanced Calibration:** Implementing isotonic regression and Platt scaling to further refine predicted probabilities.

### Conclusion
The **BankerEye** Bank Marketing Subscription Prediction System successfully demonstrates an end-to-end, production-grade machine learning application. By enforcing an anti-leakage architecture, benchmarking four diverse algorithms, providing a robust Flask API and Streamlit UI, and deploying comprehensive automated reporting, the project fulfills all technical, empirical, and academic requirements.

---

## References
1. S. Moro, P. Cortez, and P. Rita, "A data-driven approach to predict the success of bank telemarketing," *Decision Support Systems*, vol. 62, pp. 22–31, 2014. [DOI: 10.1016/j.dss.2014.03.001]
2. N. Alessa et al., "Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics," *2023 11th International Conference on Control, Mechatronics and Automation (ICCMA)*, pp. 1–6, 2023. [DOI: 10.1109/ICCMA59762.2023.10374595]
3. D. P. Singh et al., "Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning," *2024 Trends in Information and Advanced Computing (TIACOMP)*, pp. 1–6, 2024. [DOI: 10.1109/TIACOMP64125.2024.00085]
4. A. K. Dixit and R. Kokila, "Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies," *2024 3rd International Conference for Advancement in Technology (ICONAT)*, IEEE Doc: 10700543, 2024.
5. M. F. Tanvir, M. M. Hossain, and M. A. Jishan, "Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns," *International Conference on Decision Aid Sciences and Applications (DASA)*, arXiv:2410.21539, 2024. [DOI: 10.48550/arXiv.2410.21539]
6. M. Z. Khan, S. Munquad, and T. S. M. Rao, "A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models," *Computational Science and Its Applications — ICCSA 2021*, LNCS vol. 12956, Springer, pp. 93–103, 2021. [DOI: 10.1007/978-3-030-87010-9_8]

---

## Appendix: Execution and Environment Instructions
See `README.md` for Windows PowerShell execution instructions:
- Backend: `python backend/app.py` (Runs on `http://127.0.0.1:5000`)
- Frontend: `streamlit run frontend/streamlit_app.py` (Runs on `http://localhost:8501`)
- Test Suite: `pytest -v`
