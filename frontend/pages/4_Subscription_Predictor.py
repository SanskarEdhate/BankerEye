import sys
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.styling import apply_custom_css
from frontend.utils.api_client import (
    check_api_health,
    get_dataset_categories,
    predict_single,
    predict_all_models_api,
)
from frontend.components.charts import (
    render_prediction_gauge,
    render_customer_all_models_probability_bar,
    render_model_accuracy_vs_probability_bar,
)

st.set_page_config(page_title="Subscription Predictor | BankerEye ML", page_icon="🎯", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="bank-header">
        <h1>Customer Term Deposit Subscription Predictor</h1>
        <p>Pre-Campaign Customer Profiling, Multi-Model Accuracy Benchmark & Consensus Scoring</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Health Check
health = check_api_health()
if health.get("status") != "healthy":
    st.error("⚠️ Flask API is offline. Start backend via: `python backend/app.py`")
    st.stop()

if not health.get("models_trained"):
    st.warning("⚠️ Machine learning models are not trained yet. Please train them via the Dashboard or Model Comparison page.")
    st.stop()

# Anti-leakage Callout
st.markdown(
    """
    <div class="info-callout">
        <strong>Pre-Contact Predictive Assessment:</strong><br>
        Notice that call <code>duration</code> is intentionally not present in this form. In realistic bank marketing operations, 
        call duration cannot be known prior to calling. This form scores prospects strictly on verifiable pre-outreach demographics, 
        credit standing, and campaign contact history.
    </div>
    """,
    unsafe_allow_html=True,
)

# Load categories for form
categories = get_dataset_categories()

# Fallback default categories if API response missing
job_options = categories.get(
    "job",
    ["management", "technician", "blue-collar", "admin.", "services", "retired", "self-employed", "entrepreneur", "unemployed", "housemaid", "student", "unknown"]
)
marital_options = categories.get("marital", ["married", "single", "divorced"])
education_options = categories.get("education", ["secondary", "tertiary", "primary", "unknown"])
default_options = categories.get("default", ["no", "yes"])
housing_options = categories.get("housing", ["yes", "no"])
loan_options = categories.get("loan", ["no", "yes"])
contact_options = categories.get("contact", ["cellular", "telephone", "unknown"])
month_options = categories.get("month", ["may", "jul", "aug", "jun", "nov", "apr", "feb", "jan", "oct", "sep", "mar", "dec"])
poutcome_options = categories.get("poutcome", ["unknown", "failure", "other", "success"])

# Prediction Form
with st.form("prediction_form"):
    st.markdown("#### 1. Customer Demographics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        age = st.number_input("Age (years):", min_value=18, max_value=95, value=38, step=1)
    with c2:
        job = st.selectbox("Job Type:", options=job_options, index=0)
    with c3:
        marital = st.selectbox("Marital Status:", options=marital_options, index=0)
    with c4:
        education = st.selectbox("Education Level:", options=education_options, index=1)

    st.markdown("#### 2. Financial & Credit Obligations")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        balance = st.number_input("Average Annual Balance (EUR):", min_value=-5000, max_value=100000, value=2500, step=100)
    with f2:
        default = st.selectbox("Credit in Default?", options=default_options, index=0)
    with f3:
        housing = st.selectbox("Has Housing Loan?", options=housing_options, index=0)
    with f4:
        loan = st.selectbox("Has Personal Loan?", options=loan_options, index=0)

    st.markdown("#### 3. Campaign & Historical Outreach Context")
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        contact = st.selectbox("Contact Communication:", options=contact_options, index=0)
    with h2:
        day = st.number_input("Last Contact Day (1-31):", min_value=1, max_value=31, value=15, step=1)
    with h3:
        month = st.selectbox("Last Contact Month:", options=month_options, index=0)
    with h4:
        campaign = st.number_input("Campaign Contacts (this campaign):", min_value=1, max_value=50, value=1, step=1)

    h5, h6, h7, h8 = st.columns(4)
    with h5:
        pdays = st.number_input("Days Since Previous Contact (-1 = never):", min_value=-1, max_value=900, value=-1, step=1)
    with h6:
        previous = st.number_input("Previous Contacts Count:", min_value=0, max_value=50, value=0, step=1)
    with h7:
        poutcome = st.selectbox("Previous Campaign Outcome:", options=poutcome_options, index=0)
    with h8:
        model_choice = st.selectbox(
            "Evaluation Mode:",
            options=["all_models", "random_forest", "decision_tree", "logistic_regression", "knn"],
            format_func=lambda x: {
                "all_models": "🔥 Compare All 4 Models Simultaneously (Recommended)",
                "random_forest": "Random Forest Classifier",
                "decision_tree": "Decision Tree Classifier",
                "logistic_regression": "Logistic Regression",
                "knn": "K-Nearest Neighbours (KNN)",
            }.get(x, x),
            index=0,
        )

    submit_button = st.form_submit_button("⚡ Evaluate Subscription Likelihood", type="primary", use_container_width=True)

# Form Submission Processing
if submit_button:
    features_payload = {
        "age": int(age),
        "job": job,
        "marital": marital,
        "education": education,
        "default": default,
        "balance": int(balance),
        "housing": housing,
        "loan": loan,
        "contact": contact,
        "day": int(day),
        "month": month,
        "campaign": int(campaign),
        "pdays": int(pdays),
        "previous": int(previous),
        "poutcome": poutcome,
    }

    with st.spinner("Executing inference and benchmarking across all models via Flask API..."):
        all_models_resp = predict_all_models_api(features=features_payload)

    if all_models_resp.get("status") == "success":
        consensus = all_models_resp.get("consensus", {})
        models_data = all_models_resp.get("models", {})
        insights = all_models_resp.get("key_insights", [])
        disclaimer = all_models_resp.get("disclaimer")

        st.markdown("---")
        st.markdown("### 📋 Multi-Model Prediction & Accuracy Comparison")

        # Top Consensus Banner
        avg_prob_pct = consensus.get("average_probability_percentage", 50.0)
        majority_label = consensus.get("majority_outcome", "Uncertain")
        agreement_text = consensus.get("agreement_summary", "")
        risk_tier = consensus.get("risk_level", "Moderate")

        top_c1, top_c2 = st.columns([1, 1.3])

        with top_c1:
            # High-contrast probability gauge
            fig_gauge = render_prediction_gauge(
                probability=consensus.get("average_probability", 0.5),
                title_text="Consensus Subscription Probability"
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with top_c2:
            is_pos = consensus.get("majority_prediction") == 1
            box_border = "#22c55e" if is_pos else "#ef4444"
            box_bg = "rgba(34, 197, 94, 0.08)" if is_pos else "rgba(239, 68, 68, 0.08)"
            badge_bg = "#ecfdf5" if is_pos else "#fef2f2"
            badge_color = "#047857" if is_pos else "#b91c1c"

            st.markdown(
                f"""
                <div style="background: {box_bg}; border: 1.5px solid {box_border}; border-radius: 10px; padding: 20px; margin: 12px 0;">
                    <div style="font-size: 13px; color: #64748b; text-transform: uppercase; font-weight: 600;">
                        Ensemble Consensus Outcome
                        <span style="float:right; background:{badge_bg}; color:{badge_color}; padding:2px 8px; border-radius:6px; font-weight:700; font-size:12px;">{risk_tier}</span>
                    </div>
                    <div style="font-size: 24px; font-weight: 700; color: #0f172a; margin: 8px 0;">
                        {majority_label}
                    </div>
                    <div style="font-size: 14px; color: #334155; line-height: 1.6;">
                        Average Subscription Propensity: <strong>{avg_prob_pct:.1f}%</strong><br>
                        Model Agreement: <strong>{agreement_text}</strong> (4 Supervised Algorithms Evaluated)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### ⚖️ Side-by-Side Model Predictions & Benchmark Accuracies")
        st.caption("Inspect the exact prediction, probability, and test benchmark accuracy for each algorithm on this customer profile.")

        # 4 Model Cards Side by Side
        card_cols = st.columns(4)
        m_keys = ["random_forest", "decision_tree", "logistic_regression", "knn"]

        for idx, k in enumerate(m_keys):
            m = models_data.get(k, {})
            name = m.get("model_name", k).replace(" Classifier", "").replace(" (KNN)", "")
            pred_class = m.get("prediction", 0)
            prob_pct = m.get("probability_percentage", 0.0)
            acc = m.get("benchmark_accuracy")
            f1 = m.get("benchmark_f1_score")
            roc = m.get("benchmark_roc_auc")

            acc_str = f"{acc:.2%}" if acc is not None else "N/A"
            f1_str = f"{f1:.2%}" if f1 is not None else "N/A"
            roc_str = f"{roc:.2%}" if roc is not None else "N/A"

            pred_badge = (
                "<span style='background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:700; font-size:11px;'>Yes</span>"
                if pred_class == 1
                else "<span style='background:#fee2e2; color:#b91c1c; padding:2px 6px; border-radius:4px; font-weight:700; font-size:11px;'>No</span>"
            )

            with card_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 14.5px; font-weight: 700; color: #0f172a; margin-bottom: 8px;">
                            {name}
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
                            <span style="color:#64748b;">This Customer:</span>
                            <span>{pred_badge}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
                            <span style="color:#64748b;">Probability:</span>
                            <strong style="color:#2563eb;">{prob_pct:.1f}%</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
                            <span style="color:#64748b;">Test Accuracy:</span>
                            <strong style="color:#0f172a;">{acc_str}</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
                            <span style="color:#64748b;">Test F1-Score:</span>
                            <span style="color:#334155;">{f1_str}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:3px 0; font-size:12.5px;">
                            <span style="color:#64748b;">Test ROC-AUC:</span>
                            <span style="color:#334155;">{roc_str}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Comparative Visualization Tabs
        comp_tab1, comp_tab2, comp_tab3 = st.tabs([
            "📊 Propensity Comparison Chart", "📈 Accuracy vs. Customer Propensity", "📋 Detailed Comparison Table"
        ])

        with comp_tab1:
            fig_bar_compare = render_customer_all_models_probability_bar(models_data)
            st.plotly_chart(fig_bar_compare, use_container_width=True)
            st.caption("Dashed red line indicates the 50% classification decision threshold. Bars over 50% represent predicted subscribers.")

        with comp_tab2:
            fig_acc_vs_prob = render_model_accuracy_vs_probability_bar(models_data)
            st.plotly_chart(fig_acc_vs_prob, use_container_width=True)
            st.caption("Compares each algorithm's historical benchmark test accuracy against this specific customer's conversion propensity.")

        with comp_tab3:
            table_records = []
            for k in m_keys:
                m = models_data.get(k, {})
                table_records.append({
                    "Algorithm": m.get("model_name"),
                    "Prediction": m.get("outcome"),
                    "Subscription Probability": f"{m.get('probability_percentage', 0):.1f}%",
                    "Benchmark Accuracy": f"{(m.get('benchmark_accuracy') or 0):.2%}",
                    "Benchmark F1-Score": f"{(m.get('benchmark_f1_score') or 0):.2%}",
                    "Benchmark ROC-AUC": f"{(m.get('benchmark_roc_auc') or 0):.2%}",
                    "Propensity Tier": m.get("risk_level"),
                })
            st.dataframe(pd.DataFrame(table_records), use_container_width=True, hide_index=True)

        # Behavioral drivers
        if insights:
            st.markdown("##### 💡 Behavioral & Financial Driver Insights")
            for ins in insights:
                st.markdown(f"- {ins}")

        # Strict academic disclaimer
        st.markdown(
            f"""
            <div style="font-size: 11.5px; color: #64748b; margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 8px;">
                ℹ️ <strong>System Disclaimer:</strong> {disclaimer}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error(f"Prediction failed: {all_models_resp.get('message', 'Unknown error')}")
