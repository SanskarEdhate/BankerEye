import sys
from pathlib import Path
import json
import pandas as pd
import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.styling import apply_custom_css
from frontend.utils.api_client import (
    check_api_health,
    get_evaluation_report,
    download_metrics_csv_url,
    download_report_pdf_url,
)
from frontend.components.cards import render_info_banner

st.set_page_config(page_title="Reports & Insights | BankerEye ML", page_icon="📑", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="bank-header">
        <h1>Reports, Academic Insights & Literature Review</h1>
        <p>Comprehensive Empirical Assessment, SOTA Literature Synthesis, and Downloadable Evaluation Artifacts</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Health Check
health = check_api_health()
if health.get("status") != "healthy":
    st.error("⚠️ Flask API is offline. Start the backend with: `python backend/app.py`")
    st.stop()

report_data = get_evaluation_report()
if not report_data or report_data.get("status") != "success":
    st.warning("⚠️ Evaluation report is pending. Please train the models first via the Dashboard.")
    st.stop()

# Download Bar
st.markdown("### 📥 Download Official Evaluation Artifacts")
down_c1, down_c2, down_c3 = st.columns(3)

with down_c1:
    pdf_url = download_report_pdf_url()
    try:
        pdf_res = requests.get(pdf_url, timeout=10)
        if pdf_res.status_code == 200:
            st.download_button(
                label="📄 Download Academic Report (PDF)",
                data=pdf_res.content,
                file_name="Bank_Marketing_ML_Academic_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        else:
            st.error("PDF generation endpoint returned non-200.")
    except Exception as e:
        st.error(f"Could not load PDF: {e}")

with down_c2:
    csv_url = download_metrics_csv_url()
    try:
        csv_res = requests.get(csv_url, timeout=10)
        if csv_res.status_code == 200:
            st.download_button(
                label="📊 Download Metrics Comparison (CSV)",
                data=csv_res.content,
                file_name="model_metrics_comparison.csv",
                mime="text/csv",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Could not load CSV: {e}")

with down_c3:
    st.download_button(
        label="💾 Download Evaluation Summary (JSON)",
        data=json.dumps(report_data, indent=2),
        file_name="evaluation_summary.json",
        mime="application/json",
        use_container_width=True,
    )

st.markdown("---")

# Sections
r_tab1, r_tab2, r_tab3, r_tab4 = st.tabs(
    ["📚 Literature Review (5 Papers)", "⚖️ Empirical Results", "🛡️ Methodology & Anti-Leakage", "⚖️ Ethics & Limitations"]
)

# ----------------- TAB 1: LITERATURE REVIEW -----------------
with r_tab1:
    st.markdown("### Verified Scholarly Literature Review (2021–2024)")
    st.caption("Peer-reviewed research benchmarking customer response prediction on the Portuguese Bank Marketing dataset.")

    papers = [
        {
            "title": "Banking in Terms of Deposit Prediction Based on Machine Learning and Big Data Analytics",
            "authors": "Nourah Alessa, Amal Majdua, Sharifah Alshehri, Maryam Alhawiti, Resan Aljohani, A'aeshah Alhakamy",
            "year": 2023,
            "venue": "IEEE 11th International Conference on Control, Mechatronics and Automation (ICCMA)",
            "doi": "10.1109/ICCMA59762.2023.10374595",
            "url": "https://doi.org/10.1109/ICCMA59762.2023.10374595",
            "models": "Logistic Regression, Decision Tree, KNN, Random Forest, SVM + PySpark",
            "findings": "Ensemble bagging models (Random Forest) consistently surpassed individual linear classifiers in complex demographic interactions, especially when integrated with big data processing.",
            "relevance": "Evaluates the exact four core machine learning algorithms implemented in this project on the UCI Bank Marketing dataset."
        },
        {
            "title": "Enhancing Marketing Strategies: Analyzing Customer Behavior in Banking through Data Analysis and Machine Learning",
            "authors": "Davinder Paul Singh, Mani Manjari, Dipti Jain, S. B. Uppal, R. Kumar, P. Goel",
            "year": 2024,
            "venue": "IEEE Trends in Information and Advanced Computing (TIACOMP)",
            "doi": "10.1109/TIACOMP64125.2024.00085",
            "url": "https://doi.org/10.1109/TIACOMP64125.2024.00085",
            "models": "Random Forest, Decision Tree, Logistic Regression with SMOTE",
            "findings": "Addressing severe class imbalance significantly boosted subscription recall from ~30% to over 70%, preventing minority class starvation.",
            "relevance": "Confirms the necessity of our class-weighting strategy to safeguard recall on the 11.7% minority subscription class."
        },
        {
            "title": "Innovative Approaches of Machine Learning to Enhance Predictive Analytics Based on Banking Institution Strategies",
            "authors": "Anuj Kumar Dixit, R. Kokila",
            "year": 2024,
            "venue": "IEEE 3rd International Conference for Advancement in Technology (ICONAT)",
            "doi": "IEEE Document ID: 10700543",
            "url": "https://ieeexplore.ieee.org/document/10700543",
            "models": "KNN, Logistic Regression, Gaussian NB, Decision Tree, Random Forest, XGBoost, Stacking",
            "findings": "Achieved ~90.36% peak prediction accuracy through rigorous preprocessing, feature scaling, and ensemble stacking over standalone classifiers.",
            "relevance": "Directly supports our comparative findings that tuned tree ensembles yield superior discriminative capability."
        },
        {
            "title": "Bayesian Regression for Predicting Subscription to Bank Term Deposits in Direct Marketing Campaigns",
            "authors": "Muhammad Farhan Tanvir, Md Maruf Hossain, Md Asifuzzaman Jishan",
            "year": 2024,
            "venue": "International Conference on Decision Aid Sciences and Applications (DASA) / arXiv:2410.21539",
            "doi": "10.48550/arXiv.2410.21539",
            "url": "https://doi.org/10.48550/arXiv.2410.21539",
            "models": "Bayesian Logistic Regression, Probit Regression, Standard Logit",
            "findings": "Probabilistic regression formulations provide calibrated confidence intervals that prevent overconfident misallocation of banking outreach resources.",
            "relevance": "Justifies outputting well-calibrated subscription probabilities alongside discrete binary predictions in BankerEye."
        },
        {
            "title": "A Study on Improving Banking Process for Predicting Prospective Customers of Term Deposits Using Explainable Machine Learning Models",
            "authors": "Mohd Zeeshan Khan, Sana Munquad, Thota Sree Mallikharjuna Rao",
            "year": 2021,
            "venue": "Springer Lecture Notes in Computer Science (LNCS vol. 12956), ICCSA",
            "doi": "10.1007/978-3-030-87010-9_8",
            "url": "https://doi.org/10.1007/978-3-030-87010-9_8",
            "models": "Random Forest, Decision Tree, Logistic Regression, Explainable AI (SHAP)",
            "findings": "Customer financial health (account balance) and previous outreach history dominate conversion propensity; model explainability is critical for banking compliance.",
            "relevance": "Underpins our feature importance dashboard and non-causal statistical correlation explanations."
        },
    ]

    for p in papers:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                <div style="font-size: 15px; font-weight: 700; color: #0f172a;">{p['title']}</div>
                <div style="font-size: 12px; color: #64748b; margin: 4px 0;">
                    <strong>Authors:</strong> {p['authors']} ({p['year']}) | 
                    <strong>Venue:</strong> {p['venue']} | 
                    <strong>DOI:</strong> <a href="{p['url']}" target="_blank">{p['doi']}</a>
                </div>
                <div style="font-size: 13px; color: #334155; margin-top: 6px;">
                    <strong>Models Evaluated:</strong> {p['models']}<br>
                    <strong>Key Findings:</strong> {p['findings']}<br>
                    <strong>Relevance to this System:</strong> {p['relevance']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------- TAB 2: EMPIRICAL RESULTS -----------------
with r_tab2:
    st.markdown("### Empirical Four-Model Benchmark Summary")
    models_dict = report_data.get("models", {})
    if models_dict:
        table_rows = []
        for k, d in models_dict.items():
            m = d.get("metrics", {})
            cm = d.get("confusion_matrix", {})
            t = d.get("timing", {})
            table_rows.append({
                "Algorithm": d.get("display_name", k),
                "Accuracy": f"{m.get('accuracy', 0):.2%}",
                "Precision": f"{m.get('precision', 0):.2%}",
                "Recall": f"{m.get('recall', 0):.2%}",
                "F1-Score": f"{m.get('f1_score', 0):.2%}",
                "ROC-AUC": f"{m.get('roc_auc', 0):.2%}" if m.get("roc_auc") else "N/A",
                "True Negatives": f"{cm.get('true_negatives', 0):,}",
                "False Positives": f"{cm.get('false_positives', 0):,}",
                "False Negatives": f"{cm.get('false_negatives', 0):,}",
                "True Positives": f"{cm.get('true_positives', 0):,}",
                "Train Time": f"{t.get('training_time_sec', 0):.2f}s",
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Automated Qualitative Interpretation")
    for k, d in models_dict.items():
        st.markdown(f"**{d.get('display_name')}:** {d.get('interpretation')}")

# ----------------- TAB 3: METHODOLOGY & ANTI-LEAKAGE -----------------
with r_tab3:
    st.markdown("### Rigorous Preprocessing & Anti-Leakage Protocol")
    st.markdown(
        """
        1. **Feature Leakage Elimination:**  
           The original UCI dataset contains the column `duration` (last phone call duration in seconds). 
           Moro et al. specifically note that `duration` heavily influences the target (e.g. if duration=0, y='no'). 
           However, call duration is **strictly impossible to know** prior to dialing. 
           Including `duration` would introduce target leakage and make the system useless for pre-campaign outreach planning. 
           Therefore, our primary experiment completely removes `duration`.

        2. **Stratified Partitioning:**  
           Dataset partitioned strictly into 80% training (36,168 rows) and 20% test (9,043 rows) using `stratify=y` with random state 42.

        3. **Isolated Preprocessing Pipelines:**  
           All `OneHotEncoder` and `StandardScaler` transformations are fit strictly on the training partition and applied downstream 
           to the held-out test data to prevent information leakage.
        """
    )

# ----------------- TAB 4: ETHICS & LIMITATIONS -----------------
with r_tab4:
    st.markdown("### Ethical Considerations & Practical Limitations")
    st.markdown(
        """
        - **Algorithmic Bias & Fair Lending Compliance:**  
          Features like `age`, `job`, and `marital` must be monitored to ensure telemarketing offers do not discriminate 
          against protected classes under banking consumer protection regulations.
        - **Correlation vs. Causation:**  
          Statistical feature importance rankings indicate associative relationships within historical observations, 
          not direct causation.
        - **Decision-Support Role:**  
          Predictions serve to prioritize outbound contact sequences, not to automatically deny banking services or products.
        """
    )
