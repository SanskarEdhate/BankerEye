import sys
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.styling import apply_custom_css
from frontend.utils.api_client import (
    check_api_health,
    get_dataset_summary,
    get_model_comparison,
    trigger_model_training,
)
from frontend.components.cards import render_kpi_card, render_info_banner
from frontend.components.charts import (
    render_target_distribution_chart,
    render_grouped_metrics_bar,
)

try:
    st.set_page_config(page_title="Dashboard | BankerEye ML", page_icon="📊", layout="wide")
except Exception:
    pass
apply_custom_css()

st.markdown(
    """
    <div class="bank-header">
        <h1>Executive Dashboard</h1>
        <p>Operational Overview, Class Distributions, and Machine Learning Performance Indicators</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Status Verification
health = check_api_health()
if health.get("status") != "healthy":
    st.error(
        f"⚠️ Flask Backend API is currently offline. Please start it using: `python backend/app.py`"
    )
    st.stop()

# Load summary & model data
summary = get_dataset_summary()
comparison = get_model_comparison()

if not summary:
    st.warning("Could not retrieve dataset summary from API.")
    st.stop()

# Training Trigger if not trained
models_trained = comparison and comparison.get("status") == "ready" and comparison.get("models")

# Top KPI Row
k1, k2, k3, k4 = st.columns(4)

with k1:
    render_kpi_card(
        label="Dataset Population",
        value=f"{summary.get('total_rows', 0):,}",
        subtext="Historical campaign records",
        badge_text="Cleaned",
        badge_type="info",
    )

with k2:
    render_kpi_card(
        label="Input Features Used",
        value=str(len(summary.get("columns", [])) - 2),  # Excludes duration and y
        subtext="Excludes 'duration' (anti-leakage)",
        badge_text="15 Features",
        badge_type="info",
    )

with k3:
    pos_rate = summary.get("target_distribution", {}).get("yes", {}).get("percentage", 11.7)
    render_kpi_card(
        label="Subscription Rate",
        value=f"{pos_rate:.1f}%",
        subtext="Positive class imbalance",
        badge_text="5,289 Yes",
        badge_type="warning",
    )

with k4:
    if models_trained:
        raw_name = comparison.get("rankings", {}).get("roc_auc", [{}])[0].get("display_name", "Random Forest")
        best_model = raw_name.replace(" Classifier", "").replace(" (KNN)", "")
        render_kpi_card(
            label="Top Performing Model",
            value=best_model,
            subtext="Ranked by ROC-AUC",
            badge_text="4 Models Ready",
            badge_type="success",
        )
    else:
        render_kpi_card(
            label="Model Status",
            value="Not Trained",
            subtext="Click button below to train",
            badge_text="Pending",
            badge_type="warning",
        )

# Notice banner
render_info_banner(
    "Data Scope: The 45,211 records represent historical direct telemarketing campaign contacts from the UCI Bank Marketing "
    "dataset (Moro et al.). They reflect observational phone outreach outcomes, not real-time transactional bank clients.",
    title="Data Scope Notice"
)

# Main Grid: Class Imbalance Donut + Model Benchmark Preview
col_left, col_right = st.columns([1, 1.55])

with col_left:
    st.markdown("#### Campaign Conversion Distribution")
    target_dist = summary.get("target_distribution", {})
    if target_dist:
        fig_donut = render_target_distribution_chart(target_dist)
        st.plotly_chart(fig_donut, use_container_width=True)
    st.caption(
        "Notice the heavy 88.3% non-subscriber majority. In retail banking, predicting the rare 11.7% "
        "subscribers requires optimizing F1-score and Recall over raw Accuracy."
    )

with col_right:
    st.markdown("#### Model Performance Preview")
    if models_trained:
        fig_bar = render_grouped_metrics_bar(comparison.get("models", {}), compact=True)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Machine learning models have not been trained yet. Click below to execute the complete training pipeline.")
        if st.button("🚀 Train All 4 Models Now", type="primary"):
            with st.spinner("Training Logistic Regression, Decision Tree, KNN, and Random Forest on held-out test data..."):
                resp = trigger_model_training()
                if resp.get("status") == "success":
                    st.success("Training complete! Refreshing dashboard...")
                    st.rerun()
                else:
                    st.error(f"Training failed: {resp.get('message')}")

st.markdown("---")
st.markdown("#### Quick Actions & Workflow")

act1, act2, act3 = st.columns(3)

with act1:
    with st.container(border=True):
        st.markdown("##### 🔍 Explore Dataset")
        st.caption("Inspect categorical distributions, numerical ranges, missing values, and leakage prevention.")
        st.page_link("views/2_Dataset_Explorer.py", label="Open Dataset Explorer →", width="stretch")

with act2:
    with st.container(border=True):
        st.markdown("##### ⚖️ Compare Models")
        st.caption("Evaluate ROC-AUC, precision-recall trade-offs, confusion matrices, and training latencies.")
        st.page_link("views/3_Model_Comparison.py", label="Open Model Comparison →", width="stretch")

with act3:
    with st.container(border=True):
        st.markdown("##### 🎯 Make Predictions")
        st.caption("Input prospective customer parameters to obtain immediate term deposit subscription probabilities.")
        st.page_link("views/4_Subscription_Predictor.py", label="Open Subscription Predictor →", width="stretch")
