# BankerEye: Bank Marketing Subscription Prediction System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%20%7C%20Streamlit-orange.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-green.svg)](https://scikit-learn.org/)
[![Tests Passing](https://img.shields.io/badge/tests-34%20passed-brightgreen.svg)]()

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
- **Dual Inference Engine:**
  - *Interactive Profiler:* Form-based single-customer scoring with dynamic conversion probability gauges and behavioral driver insights.
  - *Bulk CSV Batch Processor:* High-throughput multi-row CSV upload with real-time conversion summaries and exportable scored files.
- **Full-Stack Decoupled Architecture:** Modular Flask REST API backend paired with a responsive Streamlit analytics dashboard.
- **Automated Academic Reporting:** Dynamically generates structured evaluation JSON, comparative CSV metrics, and formal PDF evaluation reports via ReportLab.
- **Comprehensive Pytest Suite:** 34 automated unit and integration tests covering preprocessing, model training, prediction validation, and API routes.

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
        | - Duration Exclusion Guard    |             | - Single & Batch Predictors   |
        | - ColumnTransformer Pipeline  |             | - Probability Calibration     |
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

| Algorithm | Accuracy | Precision (yes) | Recall (yes) | F1-Score (yes) | ROC-AUC | Training Time | Latency |
|---|---|---|---|---|---|---|---|
| **Random Forest** | 81.43% | 32.55% | 59.26% | 42.08% | **79.46%** | 3.25s | 45.2ms |
| **Decision Tree** | 80.38% | 32.14% | **62.48%** | **42.18%** | 75.02% | 0.28s | 8.5ms |
| **Logistic Regression** | 75.48% | 26.62% | 62.38% | 37.32% | 77.22% | 0.51s | 3.5ms |
| **KNN Classifier** | **87.15%** | 39.40% | 22.87% | 28.94% | 72.66% | 0.12s | 340.0ms |

### Key Analytical Takeaways
- **The Accuracy Paradox:** KNN attained the highest raw accuracy (87.15%) because it biased heavily toward the 88.3% majority class, but it missed over 77% of actual depositors (Recall: 22.87%).
- **Ensemble Dominance:** Random Forest delivered the highest discriminative power (ROC-AUC: 79.46%).
- **Balanced Harmonic Lead:** Decision Tree delivered top F1-Score (42.18%) and top Recall (62.48%), capturing the largest proportion of viable depositors.

---

## 📚 Verified Literature Review
This system incorporates empirical insights from five verified peer-reviewed research papers (2021–2024):
1. **Alessa et al. (2023)** — *Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics*, IEEE ICCMA, [DOI: 10.1109/ICCMA59762.2023.10374595](https://doi.org/10.1109/ICCMA59762.2023.10374595).
2. **Singh et al. (2024)** — *Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning*, IEEE TIACOMP, [DOI: 10.1109/TIACOMP64125.2024.00085](https://doi.org/10.1109/TIACOMP64125.2024.00085).
3. **Dixit & Kokila (2024)** — *Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies*, IEEE ICONAT, [IEEE Doc: 10700543](https://ieeexplore.ieee.org/document/10700543).
4. **Tanvir et al. (2024)** — *Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns*, IEEE DASA / arXiv, [DOI: 10.48550/arXiv.2410.21539](https://doi.org/10.48550/arXiv.2410.21539).
5. **Khan et al. (2021)** — *A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models*, Springer LNCS, [DOI: 10.1007/978-3-030-87010-9_8](https://doi.org/10.1007/978-3-030-87010-9_8).

---

## 📁 Project Directory Structure
```
bank-marketing-ml/
├── dataset/
│   ├── bank-full.csv                  # Canonical 45,211 row dataset (semicolon delimited)
│   ├── bank.csv                       # 10% test sample (4,521 rows)
│   └── bank-names.txt                 # Official UCI attribute documentation
├── backend/
│   ├── __init__.py
│   ├── app.py                         # Flask application factory, CORS, health route
│   ├── config.py                      # System paths, constants, environment settings
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dataset_routes.py          # /api/dataset/summary, /api/dataset/sample
│   │   ├── model_routes.py            # /api/models/train, /api/models/compare, metrics
│   │   ├── prediction_routes.py       # /api/predict, /api/predict/batch
│   │   └── report_routes.py           # /api/reports/evaluation, /api/reports/pdf
│   ├── services/
│   │   ├── __init__.py
│   │   ├── preprocessing.py           # Delimiter sniffer, ColumnTransformer, split
│   │   ├── train_models.py            # 4 pipeline trainers, metric evaluator, joblib
│   │   ├── prediction.py              # Validation, inference, probabilities
│   │   └── report_service.py          # ReportLab PDF and metrics CSV generator
│   └── saved_models/
│       ├── logistic_regression_pipeline.joblib
│       ├── decision_tree_pipeline.joblib
│       ├── knn_pipeline.joblib
│       ├── random_forest_pipeline.joblib
│       ├── model_metrics.json
│       └── evaluation_summary.json
├── frontend/
│   ├── streamlit_app.py               # Landing page, sidebar branding, system status
│   ├── pages/
│   │   ├── 1_Dashboard.py             # Top KPIs, class donut chart, quick actions
│   │   ├── 2_Dataset_Explorer.py      # Data preview, schema, descriptive stats, EDA
│   │   ├── 3_Model_Comparison.py      # 4 cards, metric rankings, ROC, confusion matrix
│   │   ├── 4_Subscription_Predictor.py# Customer input form, gauge chart, insights
│   │   ├── 5_Batch_Prediction.py      # Bulk CSV upload, summary, exportable results
│   │   └── 6_Reports_and_Insights.py  # Literature review, PDF/CSV download center
│   ├── components/
│   │   ├── __init__.py
│   │   ├── cards.py                   # KPI metric cards, info callout banners
│   │   └── charts.py                  # Plotly ROC curves, bars, confusion matrices
│   └── utils/
│       ├── __init__.py
│       ├── api_client.py              # Requests wrapper with timeouts and fallbacks
│       └── styling.py                 # Custom CSS banking analytics theme
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest test fixtures and client setup
│   ├── test_preprocessing.py          # Delimiter, loading, anti-leakage checks
│   ├── test_models.py                 # Pipeline loading, metrics integrity
│   ├── test_prediction.py             # Single & batch inference, validation
│   └── test_api.py                    # Flask HTTP routes, status codes
├── reports/
│   ├── academic_project_report.md     # 22-section comprehensive college report
│   ├── academic_evaluation_report.pdf # Generated PDF evaluation document
│   └── literature_review.md           # Deep-dive 5 paper comparison matrix
├── requirements.txt                   # Verified dependency versions
├── .env.example                       # Environment template
├── .gitignore                         # Clean git repository hygiene
└── README.md                          # Complete system documentation
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
```

### Step 2: Start the Flask Backend API (Terminal 1)
```powershell
.\venv\Scripts\Activate.ps1
python backend/app.py
```
*The API will start and listen on `http://127.0.0.1:5000`.*

### Step 3: Start the Streamlit Analytics UI (Terminal 2)
Open a second PowerShell window:
```powershell
.\venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```
*The Streamlit web dashboard will open in your browser at `http://localhost:8501`.*

> **Important Note:** Both the Flask backend and the Streamlit frontend must be running simultaneously for full operational functionality.

---

## 📡 REST API Endpoint Reference

### Operational & Dataset Endpoints
- `GET /api/health` — Verifies API health, dataset availability, and trained model status.
- `GET /api/dataset/summary` — Returns row/col counts, datatypes, missing values, and class distributions.
- `GET /api/dataset/sample?limit=10` — Returns a bounded preview of dataset records.

### Model & Training Endpoints
- `POST /api/models/train` — Retrains all four models under stratified split and saves evaluation artifacts.
  ```json
  { "test_size": 0.20, "force_retrain": true }
  ```
- `GET /api/models/compare` — Returns actual evaluation metrics, ROC curve data, and rankings.
- `GET /api/models/{model_name}/metrics` — Returns metrics and confusion matrix for a specific model (`random_forest`, `decision_tree`, `logistic_regression`, `knn`).
- `GET /api/models/feature-importance` — Returns top predictive features with non-causal disclaimer.

### Inference Endpoints
- `POST /api/predict` — Evaluates a single customer profile:
  ```json
  {
    "model": "random_forest",
    "features": {
      "age": 42,
      "job": "management",
      "marital": "married",
      "education": "tertiary",
      "default": "no",
      "balance": 3200,
      "housing": "no",
      "loan": "no",
      "contact": "cellular",
      "day": 18,
      "month": "aug",
      "campaign": 1,
      "pdays": -1,
      "previous": 0,
      "poutcome": "unknown"
    }
  }
  ```
- `POST /api/predict/batch` — Accepts array of customer dictionaries or multipart CSV upload for batch inference.

### Report Download Endpoints
- `GET /api/reports/evaluation` — Returns structured JSON evaluation summary.
- `GET /api/reports/metrics-csv` — Downloads comparative metrics CSV table.
- `GET /api/reports/pdf` — Downloads formal academic PDF evaluation report.

---

## 🧪 Running Automated Tests
The repository includes a comprehensive 34-test suite built with Pytest:
```powershell
python -m pytest -v
```
All 34 tests validate dataset integrity, delimiter detection, leakage prevention, model pipelines, input boundaries, batch prediction, and Flask API endpoints.

---

## 🔧 Troubleshooting Guide
1. **Flask API Offline in Streamlit:**  
   Ensure `python backend/app.py` is actively running in Terminal 1 on port 5000. Verify the health status via `http://127.0.0.1:5000/api/health`.
2. **Missing Dataset Error:**  
   Confirm `bank-full.csv` is present in the `dataset/` directory. If using a custom path, configure `DATASET_PATH` in `.env`.
3. **PowerShell Script Execution Policy Warning:**  
   If activating the virtual environment throws an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

---

## 📜 License & Academic Citation
Developed for academic assessment and educational research under the MIT License.

```bibtex
@article{moro2014data,
  title={A data-driven approach to predict the success of bank telemarketing},
  author={Moro, S{\'e}rgio and Cortez, Paulo and Rita, Paulo},
  journal={Decision Support Systems},
  volume={62},
  pages={22--31},
  year={2014},
  publisher={Elsevier}
}
```
