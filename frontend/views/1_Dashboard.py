import sys
import time
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import (
    check_api_health,
    get_dataset_summary,
    get_model_comparison,
    trigger_model_training,
    get_training_status,
    clear_all_api_caches,
)
from frontend.components.cards import render_kpi_card, render_info_banner
from frontend.components.charts import (
    render_target_distribution_chart,
    render_grouped_metrics_bar,
)

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

models_trained = comparison and comparison.get("status") == "ready" and bool(comparison.get("models"))
split_info = comparison.get("split_info", {}) if comparison else {}

# Top KPI Row
k1, k2, k3, k4 = st.columns(4)

with k1:
    tot_rows = summary.get("total_rows")
    val_pop = f"{tot_rows:,}" if tot_rows is not None else "Not loaded"
    render_kpi_card(
        label="Total Population",
        value=val_pop,
        subtext="Historical campaign records",
        badge_text="Cleaned",
        badge_type="info",
    )

with k2:
    if models_trained:
        feats = split_info.get("features_used", [])
        if feats:
            feat_val = str(len(feats))
        else:
            feat_val = str(split_info.get("feature_count", "N/A"))
        feat_badge = f"{feat_val} Features"
    else:
        feat_val = "Not trained"
        feat_badge = "Pending"

    render_kpi_card(
        label="Input Features",
        value=feat_val,
        subtext="Excludes 'duration' (anti-leakage)",
        badge_text=feat_badge,
        badge_type="info" if models_trained else "warning",
    )

with k3:
    target_dist = summary.get("target_distribution", {})
    pos_key = "yes" if "yes" in target_dist else ("1" if "1" in target_dist else (min(target_dist.keys(), key=lambda k: target_dist[k].get("count", 0)) if target_dist else None))
    neg_key = [k for k in target_dist.keys() if k != pos_key][0] if (target_dist and pos_key and len(target_dist) > 1) else None

    if pos_key and pos_key in target_dist:
        pos_count = target_dist[pos_key].get("count", 0)
        pos_rate = target_dist[pos_key].get("percentage", 0.0)
        neg_rate = target_dist[neg_key].get("percentage", 0.0) if neg_key else round(100.0 - pos_rate, 1)
        sub_rate_str = f"{pos_rate:.1f}%"
        sub_badge = f"{pos_count:,} {pos_key.title()}"
    else:
        pos_rate = 0.0
        neg_rate = 0.0
        sub_rate_str = "N/A"
        sub_badge = "Class Imbalance"

    render_kpi_card(
        label="Subscription Rate",
        value=sub_rate_str,
        subtext="Positive class imbalance",
        badge_text=sub_badge,
        badge_type="warning",
    )

with k4:
    if models_trained:
        raw_name = comparison.get("rankings", {}).get("roc_auc", [{}])[0].get("display_name", "Random Forest")
        best_model = raw_name.replace(" Classifier", "").replace(" (KNN)", "")
        render_kpi_card(
            label="Top Model",
            value=best_model,
            subtext="Ranked by test ROC-AUC",
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
    "Data Scope: The records represent historical direct telemarketing campaign contacts from the UCI Bank Marketing "
    "dataset (Moro et al.). They reflect observational phone outreach outcomes, not real-time transactional bank clients.",
    title="Data Scope Notice"
)

# Main Grid: Class Imbalance Donut + Model Benchmark Preview
col_left, col_right = st.columns([1, 1.55])

with col_left:
    st.markdown("#### Campaign Conversion Distribution")
    if target_dist:
        fig_donut = render_target_distribution_chart(target_dist)
        st.plotly_chart(fig_donut, width="stretch")
    st.caption(
        f"Notice the heavy {neg_rate:.1f}% non-subscriber majority. In retail banking, predicting the rare {pos_rate:.1f}% "
        "subscribers requires optimizing F1-score and Recall over raw Accuracy."
    )

with col_right:
    st.markdown("#### Model Performance Preview")
    if models_trained:
        fig_bar = render_grouped_metrics_bar(comparison.get("models", {}), compact=True)
        st.plotly_chart(fig_bar, width="stretch")
    else:
        st.info("Machine learning models have not been trained yet. Click below to execute the complete training pipeline.")
        if st.button("🚀 Train All 4 Models Now", type="primary", width="stretch"):
            resp = trigger_model_training()
            if resp.get("status") in ("training_started", "busy"):
                job_id = resp.get("job_id", "")
                progress_bar = st.progress(0)
                status_container = st.empty()
                status_container.info("Training background job dispatched. Initializing pipeline...")

                done = False
                while not done:
                    time.sleep(1.2)
                    st_info = get_training_status()
                    curr_state = st_info.get("state", "unknown")
                    curr_prog = int(st_info.get("progress", 0))
                    progress_bar.progress(min(curr_prog, 100))
                    status_container.info(f"Training status ({curr_prog}%): {st_info.get('message', 'Computing...')}")

                    if curr_state == "done":
                        clear_all_api_caches()
                        progress_bar.progress(100)
                        status_container.success("All 4 models successfully trained and calibrated! Refreshing dashboard...")
                        time.sleep(1)
                        st.rerun()
                        done = True
                    elif curr_state == "failed":
                        status_container.error(f"Training job failed: {st_info.get('error', 'Unknown failure')}")
                        done = True
            else:
                st.error(f"Failed to initiate training: {resp.get('message')}")

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
