import sys
import json
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import (
    check_api_health,
    get_evaluation_report,
    fetch_metrics_csv_bytes,
    fetch_report_pdf_bytes,
)

st.markdown(
    """
    <div class="bank-header">
        <h1>Evaluation Reports & Academic Insights</h1>
        <p>Comprehensive Empirical Benchmarks, Verified Scholarly Literature, and Exportable Deliverables</p>
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

# Download Bar with cached bytes
st.markdown("### 📥 Download Official Evaluation Artifacts")
down_c1, down_c2, down_c3 = st.columns(3)

with down_c1:
    pdf_bytes = fetch_report_pdf_bytes()
    if pdf_bytes:
        st.download_button(
            label="📄 Academic Report (PDF)",
            data=pdf_bytes,
            file_name="Bank_Marketing_ML_Academic_Report.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch",
        )
    else:
        st.button("📄 Academic Report PDF (Pending)", disabled=True, width="stretch")

with down_c2:
    csv_bytes = fetch_metrics_csv_bytes()
    if csv_bytes:
        st.download_button(
            label="📊 Metrics Comparison (CSV)",
            data=csv_bytes,
            file_name="model_metrics_comparison.csv",
            mime="text/csv",
            width="stretch",
        )
    else:
        st.button("📊 Metrics CSV (Pending)", disabled=True, width="stretch")

with down_c3:
    st.download_button(
        label="💾 Evaluation Summary (JSON)",
        data=json.dumps(report_data, indent=2),
        file_name="evaluation_summary.json",
        mime="application/json",
        width="stretch",
    )

st.markdown("---")

# Sections
r_tab1, r_tab2, r_tab3, r_tab4 = st.tabs(
    ["📚 Literature Review", "⚖️ Empirical Results", "🛡️ Methodology & Anti-Leakage", "⚖️ Ethics & Limitations"]
)

# ----------------- TAB 1: LITERATURE REVIEW (Single Source of Truth) -----------------
with r_tab1:
    st.markdown("### Scholarly Literature Review & Citation Audit")
    st.caption("Peer-reviewed research benchmarking customer response prediction on the Portuguese Bank Marketing dataset.")

    lit_json_path = BASE_DIR / "reports" / "literature_data.json"
    papers = []
    if lit_json_path.exists():
        try:
            with open(lit_json_path, "r", encoding="utf-8") as f:
                papers = json.load(f)
        except Exception as e:
            st.error(f"Failed to load literature_data.json: {e}")

    if not papers:
        st.warning("Literature review data file not found or empty.")
    else:
        for p in papers:
            is_verified = (p.get("verification_status") == "Verified")
            badge_class = "badge-success" if is_verified else "badge-warning"
            status_text = p.get("verification_status", "Unverified, check before citing")

            with st.container(border=True):
                c_head1, c_head2 = st.columns([3, 1])
                with c_head1:
                    st.markdown(f"#### {p.get('id', '')}. {p.get('title')}")
                with c_head2:
                    st.markdown(
                        f"""<div style="text-align: right; padding-top: 6px;">
                            <span class="badge {badge_class}">{status_text}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"""
                    **Authors:** {p.get('authors')} ({p.get('year')})  
                    **Venue / Publisher:** {p.get('venue')}  
                    **Identifier / Link:** [{p.get('doi')}]({p.get('url')})  
                    **Models Investigated:** `{p.get('models')}`  
                    
                    **Key Research Findings:**  
                    {p.get('findings')}  
                    
                    **Direct Relevance to BankerEye Architecture:**  
                    {p.get('relevance')}
                    """
                )

# ----------------- TAB 2: EMPIRICAL RESULTS -----------------
with r_tab2:
    st.markdown("### Four-Model Empirical Performance Comparison")
    models_dict = report_data.get("models", {})
    model_keys = ["logistic_regression", "decision_tree", "knn", "random_forest"]

    if models_dict:
        table_rows = []
        for k in model_keys:
            d = models_dict.get(k, {})
            m = d.get("metrics", {})
            t = d.get("timing", {})
            cm = d.get("confusion_matrix", {})
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
        st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

    st.markdown("#### Automated Qualitative Interpretation")
    for k, d in models_dict.items():
        st.markdown(f"**{d.get('display_name')}:** {d.get('description', '')}")

# ----------------- TAB 3: METHODOLOGY & ANTI-LEAKAGE -----------------
with r_tab3:
    st.markdown("### Rigorous Preprocessing & Anti-Leakage Protocol")
    split_info = report_data.get("experimental_split", {})
    train_count = split_info.get("train_rows", 0)
    test_count = split_info.get("test_rows", 0)
    test_sz = split_info.get("test_size", 0.20)
    rnd_st = split_info.get("random_state", 42)

    st.markdown(
        f"""
        1. **Feature Leakage Elimination:**  
           The benchmark bank marketing dataset contains the column `duration` (last phone call duration in seconds). 
           Moro et al. specifically note that `duration` heavily influences the target (e.g. if duration=0, y='no'). 
           However, call duration is **strictly impossible to know** prior to dialing. 
           Including `duration` would introduce target leakage and make the system useless for pre-campaign outreach planning. 
           Therefore, our primary experiment completely removes `duration`.

        2. **Stratified Partitioning:**  
           Dataset partitioned strictly into {(1.0 - test_sz):.0%} training ({train_count:,} rows) and {test_sz:.0%} test ({test_count:,} rows) using `stratify=y` with random state {rnd_st}.

        3. **Isolated Preprocessing Pipelines:**  
           All `OneHotEncoder`, `StandardScaler`, and `PdaysFeatureEngineer` transformations are fit strictly on the training partition and applied downstream 
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
