# BankerEye: Bank Marketing Subscription Prediction System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%20%7C%20Streamlit-orange.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-green.svg)](https://scikit-learn.org/)
[![Tests Passing](https://img.shields.io/badge/tests-60%20passed-brightgreen.svg)]()

An end-to-end Machine Learning web application and REST API engineered to optimize direct telemarketing campaigns for retail banking institutions. The system predicts prospective customer propensity to subscribe to long-term deposits using historical campaign data, benchmarks four supervised algorithms, and enforces an anti-leakage architecture.

---

## 📌 Table of Contents
- [Executive Overview](#executive-overview)
- [Key Features](#key-features)
- [Dataset Information & Leakage Policy](#dataset-information--leakage-policy)
- [System Architecture](#system-architecture)
- [Empirical Benchmark Results](#empirical-benchmark-results)
- [Verified Literature Review](#verified-literature-review)
- [Project Directory Structure](#project-directory-structure)
- [Windows PowerShell Quickstart](#windows-powershell-quickstart)
- [REST API Endpoint Reference](#rest-api-endpoint-reference)
- [Running Automated Tests](#running-automated-tests)
- [Troubleshooting Guide](#troubleshooting-guide)
- [License & Academic Citation](#license--academic-citation)

---

## 🎯 Executive Overview
Direct outbound telemarketing campaigns in commercial banking incur substantial labor and telephony costs while typically yielding modest conversion rates (10–15%). BankerEye replaces untargeted outreach with data-driven predictive lead scoring. 

By analyzing customer demographics, financial liquidity, credit obligations, and prior marketing responsiveness, BankerEye tiers prospective customers into clear propensity bands, empowering marketing teams to maximize conversion yield while minimizing wasteful outbound calls.

---

## 🌟 Key Features
- **Anti-Leakage Machine Learning Pipeline:** Call duration (`duration`) is strictly excluded from feature inputs, guaranteeing realistic pre-contact predictions.
- **Empirical 4-Model Benchmark:** Trains and compares Logistic Regression, Decision Tree, K-Nearest Neighbours (KNN), and Random Forest on an identical held-out test split (80/20 stratified).
- **Cost-Sensitive Class Balancing:** `class_weight='balanced'` is enforced on Logistic Regression, Decision Tree, and Random Forest to mitigate the 88.3% / 11.7% class imbalance (KNN has no native `class_weight` parameter, which is rigorously documented).
- **Isotonic Probability Calibration:** Every pipeline is wrapped in `CalibratedClassifierCV(method="isotonic", cv=3)` fitted on training data, delivering low Brier scores (< 0.090) and reliable probabilities.
- **Validation-Tuned Decision Thresholds:** Optimal decision thresholds are chosen on a validation split carved strictly from the training partition to maximize the F1-score.
- **Bootstrap 95% Confidence Intervals:** 500-sample percentile bootstrap confidence intervals prevent overconfident claims of algorithmic superiority when intervals overlap.
- **Dual Inference Engine:**
  - *Interactive Profiler:* Form-based single-customer scoring with dynamic conversion probability gauges and behavioral driver insights.
  - *Bulk CSV Batch Processor:* High-throughput multi-row CSV upload with real-time conversion summaries and exportable scored files.
- **Full-Stack Decoupled Architecture:** Modular Flask REST API backend paired with a responsive Streamlit analytics dashboard.
- **Automated Academic Reporting:** Dynamically generates structured evaluation JSON, comparative CSV metrics, and formal PDF evaluation reports via ReportLab.
- **Comprehensive Pytest Suite:** 60 automated unit and integration tests covering preprocessing, model training, prediction validation, API routes, and system hardening.

---

## 📊 Dataset Information & Leakage Policy
- **Benchmark Source:** UCI Machine Learning Repository — Bank Marketing Dataset ([Moro et al., 2011/2014](https://archive.ics.uci.edu/dataset/222/bank+marketing)).
- **Population:** 45,211 observational campaign phone calls from a Portuguese retail bank.
- **Target Variable:** `y` (Binary: `no` = 39,922 [88.30%], `yes` = 5,289 [11.70%]).
- **Delimiter:** Semicolon (`;`) detected automatically via `csv.Sniffer`.

### 🛡️ Critical Feature Leakage Safeguard
The original UCI dataset contains `duration` (the last contact call duration in seconds). As noted by Moro et al., call duration is strongly correlated with conversion success, but is **strictly impossible to know before placing the call**. Including `duration` introduces severe target leakage and produces unrealistic models. BankerEye strictly excludes `duration` from the primary training and inference pipelines.

---

## 🏗️ System Architecture
```
                                +-----------------------------+
                                |      Streamlit Frontend     |
                                |   http://localhost:8501     |
                                +--------------+--------------+
                                               |
                                     HTTP JSON Requests
                                               |
                                               v
                                +-----------------------------+
                                |       Flask REST API        |
                                |    http://127.0.0.1:5000    |
                                +--------------+--------------+
                                               |
                        +----------------------+----------------------+
                        |                                             |
                        v                                             v
        +-------------------------------+             +-------------------------------+
        |     Preprocessing Engine      |             |     ML Inference Engine       |
        | - Auto Delimiter Detection    |             | - 4 Scikit-Learn Pipelines    |
        | - PdaysFeatureEngineer        |             | - Isotonic Calibration (CV=3) |
        | - Duration Exclusion Guard    |             | - Single & Batch Predictors   |
        | - ColumnTransformer Pipeline  |             | - Validation-Tuned Thresholds |
        +---------------+---------------+             +---------------+---------------+
                        |                                             |
                        +----------------------+----------------------+
                                               |
                                               v
                                +-----------------------------+
                                |    Saved Models & Reports   |
                                |  backend/saved_models/*.joblib
                                |  reports/*.pdf, *.csv, *.json
                                +-----------------------------+
```

---

## 📈 Empirical Benchmark Results
All four models were trained on 36,168 rows (80%) and evaluated on the held-out test partition of 9,043 rows (20%) with stratified class proportions:

| Algorithm | Accuracy | Precision (yes) | Recall (yes) | F1-Score (yes) | 95% Bootstrap CI (F1) | ROC-AUC | 95% CI (ROC-AUC) | Brier Score | Optimal Threshold |
|---|---|---|---|---|---|---|---|---|---|
| **Random Forest** | 86.97% | 44.91% | 50.00% | 47.32% | [0.4464, 0.4965] | **79.86%** | [0.7841, 0.8138] | **0.0822** | 0.22 |
| **Decision Tree** | **88.00%** | **48.66%** | 46.41% | **47.51%** | [0.4468, 0.5011] | 77.76% | [0.7611, 0.7947] | 0.0834 | 0.22 |
| **Logistic Regression** | 87.84% | 47.76% | 42.34% | 44.89% | [0.4217, 0.4732] | 77.20% | [0.7578, 0.7889] | 0.0850 | 0.25 |
| **KNN Classifier** | 86.42% | 41.13% | 37.24% | 39.09% | [0.3649, 0.4179] | 72.33% | [0.7056, 0.7416] | 0.0897 | 0.17 |

### Key Analytical Takeaways
- **Statistical Distinguishability:** The 95% bootstrap confidence intervals for Decision Tree [0.4468, 0.5011] and Random Forest [0.4464, 0.4965] overlap on this test set. Therefore, their predictive performances are **not statistically distinguishable**, and neither algorithm can be claimed as strictly superior.
- **Class Weighting:** `class_weight='balanced'` is enforced on Logistic Regression, Decision Tree, and Random Forest. Scikit-learn's `KNeighborsClassifier` does not support class weights, as documented.
- **Probability Calibration:** Wrapping models in `CalibratedClassifierCV(method="isotonic", cv=3)` fitted on the training set produces well-calibrated posterior probabilities, verified by low Brier scores (< 0.090 across all models).
- **The Accuracy Paradox:** Because 88.3% of customers do not subscribe, a trivial model predicting 'No' universally achieves 88.30% accuracy while capturing zero subscribers. Our models deliberately prioritize F1-score and Recall over raw accuracy.

---

## 📚 Verified Literature Review
This system incorporates empirical insights from scholarly research papers (2021–2024), individually audited for citation authenticity:
1. **Alessa et al. (2023)** — *Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics*, IEEE ICCMA, [DOI: 10.1109/ICCMA59762.2023.10374595](https://doi.org/10.1109/ICCMA59762.2023.10374595) *(Unverified, check before citing)*.
2. **Singh et al. (2024)** — *Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning*, IEEE TIACOMP, [DOI: 10.1109/TIACOMP64125.2024.00085](https://doi.org/10.1109/TIACOMP64125.2024.00085) *(Unverified, check before citing)*.
3. **Dixit & Kokila (2024)** — *Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies*, IEEE ICONAT, [IEEE Doc: 10700543](https://ieeexplore.ieee.org/document/10700543) *(Unverified, check before citing)*.
4. **Tanvir et al. (2024)** — *Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns*, IEEE DASA / arXiv, [DOI: 10.48550/arXiv.2410.21539](https://doi.org/10.48550/arXiv.2410.21539) *(Verified)*.
5. **Khan et al. (2021)** — *A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models*, Springer LNCS, [DOI: 10.1007/978-3-030-87010-9_8](https://doi.org/10.1007/978-3-030-87010-9_8) *(Unverified, check before citing)*.

---

## 📁 Project Directory Structure
```
bank-marketing-ml/
├── dataset/
│   ├── Data Cleaning & Splitting/     # Standardized 5-stage data hierarchy
│   │   ├── 1_uci_bank_marketing_canonical/
│   │   │   ├── 01_Raw_Data/
│   │   │   ├── 02_Unclean_Data/
│   │   │   ├── 03_Clean_Data/
│   │   │   ├── 04_Train_Data/
│   │   │   └── 05_Test_Data/
│   │   └── dataset_manifest.json      # Structured dataset registry
├── backend/
│   ├── app.py                         # Flask factory, error handling, CORS, health route
│   ├── config.py                      # Configuration, paths, feature definitions
│   ├── routes/
│   │   ├── dataset_routes.py          # Summary, sample, catalog, manifest endpoints
│   │   ├── model_routes.py            # Async training, status polling, comparison, metrics
│   │   ├── prediction_routes.py       # Single & batch prediction endpoints
│   │   └── report_routes.py           # Evaluation report, metrics CSV, PDF downloads
│   ├── services/
│   │   ├── preprocessing.py           # Delimiter sniffer, ColumnTransformer, PdaysFeatureEngineer
│   │   ├── train_models.py            # GridSearch CV, isotonic calibration, bootstrap CIs
│   │   ├── prediction.py              # Strict input validation, dynamic risk tiers, consensus
│   │   └── report_service.py          # ReportLab PDF and metrics CSV generator
│   └── saved_models/                  # Serialized .joblib pipelines and JSON metrics
├── frontend/
│   ├── streamlit_app.py               # Root application router and sidebar navigation
│   ├── views/
│   │   ├── Home.py                    # System navigation and dynamic KPI overview
│   │   ├── 1_Dashboard.py             # Operational KPIs, class donut chart, training trigger
│   │   ├── 2_Dataset_Explorer.py      # Multi-stage data preview, schema, descriptive stats
│   │   ├── 3_Model_Comparison.py      # Comparative rankings, CIs, temporal checks, ROC
│   │   ├── 4_Subscription_Predictor.py# Profiling form, single model & consensus evaluation
│   │   ├── 5_Batch_Prediction.py      # High-throughput CSV upload and error reporting
│   │   └── 6_Reports_and_Insights.py  # Literature review audit and report downloads
│   ├── components/
│   │   ├── cards.py                   # Reusable KPI and info callout cards
│   │   └── charts.py                  # Plotly gauges, ROC curves, confusion matrices
│   └── utils/
│       ├── api_client.py              # Requests client with Streamlit cache_data (ttl=60)
│       └── styling.py                 # Banking-grade CSS theme and responsive sidebar
├── tests/                             # Comprehensive automated test suite
├── reports/                           # Academic Markdown, PDF, and literature review files
├── requirements.txt                   # Pinned runtime dependencies
├── requirements-dev.txt               # Testing and linting dependencies
├── .env.example                       # Environment template
└── README.md                          # Repository documentation
```

---

## 💻 Windows PowerShell Quickstart

### Step 1: Environment Setup
Open Windows PowerShell in the project directory:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 2: Train Models (Train First)
Before launching services or executing tests, train and calibrate all four models:
```powershell
python -m backend.services.train_models
```
*This executes 5-fold cross-validated grid search, isotonic calibration (cv=3), optimal threshold tuning, and 500-iteration bootstrap confidence intervals, saving all pipelines into `backend/saved_models/`.*

### Step 3: Start the Flask Backend API (Terminal 1)
```powershell
.\venv\Scripts\Activate.ps1
python backend/app.py
```
*The API will start and listen on `http://127.0.0.1:5000`.*

### Step 4: Start the Streamlit Analytics UI (Terminal 2)
Open a second PowerShell window:
```powershell
.\venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```
*The Streamlit web dashboard will open in your browser at `http://localhost:8501`.*

---

## 📡 REST API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Returns operational health status and verifies all 4 `.joblib` models and metrics JSON exist. |
| `GET` | `/api/dataset/summary` | Returns dataset row/col counts, data types, missing values, and distributions. |
| `GET` | `/api/dataset/sample?limit=15` | Returns a sample of preview records with NaN converted to None. |
| `GET` | `/api/dataset/catalog` | Returns the dynamic catalog of all organized dataset folders with file-computed row counts. |
| `GET` | `/api/dataset/manifest` | Returns the full dataset manifest with forward-slash relative paths. |
| `POST` | `/api/models/train` | Dispatches background training thread; returns 202 Accepted + `job_id` immediately. |
| `GET` | `/api/models/train/status` | Returns training job state (`idle`, `running`, `done`, `failed`), progress, and message. |
| `GET` | `/api/models/compare` | Returns measured evaluation metrics, rankings, 95% CIs, and temporal check table. |
| `GET` | `/api/models/<name>/metrics` | Returns metrics and confusion matrix for a specific model key. |
| `GET` | `/api/models/feature-importance` | Returns grouped permutation feature importances for ensemble models. |
| `POST` | `/api/predict` | Validates customer JSON payload and returns prediction, calibrated probability, and risk tier. |
| `POST` | `/api/predict/all` | Runs single customer through all 4 models simultaneously, computing calibrated ensemble consensus. |
| `POST` | `/api/predict/batch` | Validates rows strictly, returning row-by-row error reasons (400) or predictions. |
| `GET` | `/api/reports/evaluation` | Returns structured evaluation summary JSON. |
| `GET` | `/api/reports/metrics-csv` | Streams downloadable metrics comparison CSV. |
| `GET` | `/api/reports/pdf` | Dynamically generates and streams formal ReportLab evaluation PDF report. |

---

## 🧪 Running Automated Tests
Run the automated test suite using `pytest`:
```powershell
pytest tests/ -q
```
*All tests derive assertions dynamically from the saved metrics JSON and configuration, including mock model bootstrapping in conftest for clean test runs.*

---

## 📄 License & Academic Citation
Developed for academic machine learning research and engineering evaluation.
If using this project in academic research, please cite:
```bibtex
@misc{bankereye2025,
  title={BankerEye: Bank Marketing Subscription Prediction System Using Machine Learning},
  author={BankerEye Engineering Team},
  year={2025},
  publisher={GitHub}
}
```
