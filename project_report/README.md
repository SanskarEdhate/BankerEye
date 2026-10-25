# BankerEye: Bank Marketing Subscription Prediction System
## Academic Project Report & Verification Artifacts Package

This directory (`project_report/`) contains the complete academic project documentation, experimental summaries, high-resolution figures, and live browser screenshots for the **Bank Marketing Subscription Prediction System (BankerEye)**.

---

## 📁 Deliverables Directory Structure

```text
project_report/
├── Bank_Marketing_Project_Report.docx    # Full academic report in editable Microsoft Word format (2.0 MB)
├── Bank_Marketing_Project_Report.pdf     # Production PDF generated via Microsoft Word native engine (5.9 MB)
├── report_data_summary.json             # Ground-truth dataset & evaluation statistics JSON
├── README.md                            # Comprehensive report documentation and verification guide
├── screenshots/                         # Live browser interface screenshots (Playwright Chromium)
│   ├── 01_dashboard.png                 # Main Executive Dashboard (KPIs, conversion trends)
│   ├── 02_dataset_explorer.png          # Dataset Explorer (45,211 rows × 17 columns preview)
│   ├── 03_preprocessing.png             # Multi-stage cleaning & splitting pipeline inspection
│   ├── 04_model_comparison.png          # Benchmark model comparison table
│   ├── 05_evaluation_metrics.png        # Comparative metric bar charts (Acc, Prec, Rec, F1, AUC)
│   ├── 06_confusion_matrices.png        # Empirical 2x2 confusion matrix analysis
│   ├── 07_roc_curves.png                # Multi-model ROC curves discrimination visualization
│   ├── 08_customer_prediction.png       # Live single-customer inference form & consensus output
│   ├── 09_batch_prediction.png          # Bulk CSV batch scoring engine & conversion predictions
│   └── 10_reports_interface.png         # Compliance reports & official artifact download center
└── figures/                             # High-resolution (300 DPI) academic figures & diagrams
    ├── fig_3_1_system_architecture.png  # Multi-tier system architecture diagram
    ├── fig_3_2_ml_workflow.png          # End-to-end ML & anti-leakage pipeline workflow
    ├── fig_4_1_target_distribution.png  # Target variable ('y') class distribution & imbalance
    ├── fig_6_1_model_comparison_bars.png# 4-model performance comparison bar chart
    ├── fig_6_2_precision_recall_f1.png  # Minority class precision, recall, and F1 trade-off
    ├── fig_6_3_roc_curves.png           # Multi-classifier ROC curves (AUC comparison)
    ├── fig_6_4_confusion_matrices.png   # 2x2 confusion matrix heatmaps across all 4 models
    └── fig_6_5_feature_importance.png   # Top 15 Random Forest feature importances (MDI)
```

---

## 📖 Academic Report Contents & Chapter Overview

The generated academic report (`Bank_Marketing_Project_Report.docx` and `.pdf`) strictly adheres to standard B.Tech academic guidelines and includes:

1. **Preliminary Pages**:
   - Cover Page with Project Title, Subtitle, editable Student Name, Roll Number, Guide Name, Department, Institution, and Academic Year (2025–2026).
   - Certificate of Approval (editable signatures for Guide and HOD).
   - Candidate's Declaration (editable date, place, name, and roll number).
   - Acknowledgements.
   - Formal Academic Abstract.
   - Table of Contents, List of Figures, List of Tables, and List of Abbreviations.

2. **Chapter 1: Introduction**:
   - Project background, problem statement, motivation, research objectives, scope, proposed BankerEye solution, key platform features, Python/Flask/Streamlit technology stack, practical commercial banking applications, and report organization.

3. **Chapter 2: Literature Review**:
   - Structured empirical synthesis of 5 benchmark research studies (Alessa et al., 2023; Singh et al., 2024; Dixit & Kokila, 2024; Tanvir et al., 2024; Khan et al., 2021) with methodologies, venues, key findings, and explicit literature verification statuses (Tanvir et al. marked *Verified*, remaining papers marked *Unverified, check before citing*).
   - Detailed analysis of the **Research Gap**: widespread omission of anti-leakage duration exclusion, lack of probability calibration, neglect of decision threshold tuning under extreme 88:12 class imbalance, and the absence of integrated production REST API deployments.

4. **Chapter 3: Methodology**:
   - Technical workflow: CSV delimiter detection (`csv.Sniffer`), feature/target separation, ColumnTransformer pipeline (`StandardScaler` + `OneHotEncoder`), stratified 80:20 train/test splitting, estimator fit protocols, evaluation formulation, Joblib persistence, single-customer inference, batch prediction, Flask REST API blueprint routing, and automated report generation.
   - Includes **Figure 3.1: System Architecture** and **Figure 3.2: ML Workflow Diagram**.

5. **Chapter 4: Data Cleaning and Preprocessing**:
   - Benchmark dataset provenance (Moro et al., 2014, UCI Machine Learning Repository, 45,211 rows × 17 attributes).
   - Attribute dictionary (**Table 4.1**), target distribution analysis (**Figure 4.1**), null-cell audits, 'unknown' category preservation, binary encoding, one-hot expansion (50 processed dimensions), and **anti-leakage protocol (justification for duration exclusion)**.

6. **Chapter 5: Results and Discussion**:
   - Consolidated empirical results (**Table 5.1**) and confusion matrix error decomposition (**Table 5.2**).
   - ROC-AUC analysis, model strengths/weaknesses, severe class imbalance dynamics (11.7% positive class), and commercial cost-benefit trade-offs.

7. **Chapter 6: State-of-the-Art Models Comparison**:
   - Hyperparameter configurations (**Table 6.1**) for Logistic Regression, Decision Tree, K-Nearest Neighbours, and Random Forest.
   - Comparative bar charts (**Figure 6.1**), precision/recall trade-offs (**Figure 6.2**), ROC curves (**Figure 6.3**), confusion matrices (**Figure 6.4**), and Random Forest feature importances (**Figure 6.5**).
   - Computational latencies (**Table 6.2**) and synthesis designating Random Forest as the recommended production classifier.

8. **Chapter 7: User Interface Development and Deployment**:
   - Frontend architecture and Single-Source-of-Truth design pattern.
   - **All 10 live browser screenshots embedded directly into the report** with numbered captions and detailed in-text references:
     - **Figure 7.1: Main Executive Dashboard Interface**
     - **Figure 7.2: Dataset Explorer Interface**
     - **Figure 7.3: Data Preprocessing and Partitioning Stages**
     - **Figure 7.4: Multi-Model Benchmark Comparison Table**
     - **Figure 7.5: Model Evaluation Metrics Visualization**
     - **Figure 7.6: Empirical Confusion Matrix Analysis**
     - **Figure 7.7: Multi-Classifier ROC Curves View**
     - **Figure 7.8: Single Customer Subscription Predictor**
     - **Figure 7.9: Batch Customer Scoring Engine**
     - **Figure 7.10: Executive Reports & Download Center**
   - Verified local deployment instructions, project conclusion, and future scope.

9. **Chapter 8: References**:
   - 15 standard IEEE-formatted citations covering the UCI benchmark dataset, machine learning foundations, and official software libraries (excluding Chapter 2 literature review papers).

---

## 📊 Summary of Ground-Truth Experimental Results (Calibrated & Threshold-Tuned)

| Classifier | Accuracy | Precision | Recall | F1-Score (95% CI) | ROC-AUC (95% CI) | Brier Score | Train Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 87.84% | 47.76% | 42.34% | 0.4489 [0.4217, 0.4732] | 0.7720 [0.7578, 0.7889] | 0.0850 | 5.486 s |
| **Decision Tree** | **88.00%** | **48.66%** | 46.41% | **0.4751** [0.4468, 0.5011] | 0.7776 [0.7611, 0.7947] | 0.0834 | 6.724 s |
| **K-Nearest Neighbours (KNN)** | 86.42% | 41.13% | 37.24% | 0.3909 [0.3649, 0.4179] | 0.7233 [0.7056, 0.7416] | 0.0897 | 10.785 s |
| **Random Forest (Production)** | 86.97% | 44.91% | **50.00%** | 0.4732 [0.4464, 0.4965] | **0.7986** [0.7841, 0.8138] | **0.0822** | 135.863 s |

*Evaluation performed on N = 9,043 independent held-out test samples (7,985 negative, 1,058 positive) using isotonic probability calibration (`CalibratedClassifierCV`) and validation-tuned decision thresholds. Random Forest and Decision Tree F1 95% confidence intervals overlap, rendering their F1 performances statistically indistinguishable.*

---

## 🚀 Local Reproduction & Verification Instructions

### 1. Requirements
- Python 3.11+
- Virtual environment with dependencies from `requirements.txt`

### 2. Start Services
- **Backend (Flask REST API)**:
  ```bash
  python backend/app.py
  # Endpoint: http://127.0.0.1:5000 (Health: http://127.0.0.1:5000/api/health)
  ```
- **Frontend (Streamlit UI)**:
  ```bash
  streamlit run frontend/streamlit_app.py --server.port 8501
  # Portal: http://localhost:8501
  ```

### 3. Automated Test Suite
```bash
pytest tests/ -q
# Output: 41 passed (100% test coverage)
```

### 4. Regenerate Reports and Screenshots (Optional)
```bash
python scratch/capture_all_screenshots.py
python scratch/generate_report_assets.py
python scratch/generate_academic_report.py
```

---

## ⚠️ Known Limitations & Scope Boundaries
1. **Duration Exclusion**: As required for pre-campaign operational validity, call duration is excluded. Consequently, absolute recall sits between 17% and 22%, prioritizing high precision (69.5%) to minimize unproductive calls.
2. **Local Deployment**: The platform is tested and optimized for local workstation execution (`127.0.0.1:5000` and `localhost:8501`). Cloud cluster deployment and authentication (LDAP/OAuth2) are slated for future enterprise releases.
