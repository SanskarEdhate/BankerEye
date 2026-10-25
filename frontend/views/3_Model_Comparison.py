import sys
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import (
    check_api_health,
    get_model_comparison,
    get_feature_importance,
    trigger_model_training,
)
from frontend.components.charts import (
    render_grouped_metrics_bar,
    render_roc_curves,
    render_confusion_matrix_heatmap,
    render_feature_importance_chart,
)

try:
    st.set_page_config(page_title="Model Comparison | BankerEye ML", page_icon="⚖️", layout="wide")
except Exception:
    pass

st.markdown(
    """
    <div class="bank-header">
        <h1>Empirical Model Comparison & Benchmarking</h1>
        <p>Comprehensive Evaluation of 4 Supervised Algorithms on Held-Out Test Data (80/20 Stratified Partition)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

health = check_api_health()
if health.get("status") != "healthy":
    st.error("⚠️ Flask API is offline. Start the backend with: `python backend/app.py`")
    st.stop()

comparison = get_model_comparison()
models_ready = comparison and comparison.get("status") == "ready" and comparison.get("models")

if not models_ready:
    st.info("Models have not been trained yet. Click below to train Logistic Regression, Decision Tree, KNN, and Random Forest.")
    if st.button("🚀 Train All 4 Models", type="primary"):
        with st.spinner("Training models and computing evaluation metrics..."):
            res = trigger_model_training()
            if res.get("status") == "success":
                st.success("Models successfully trained!")
                st.rerun()
            else:
                st.error(f"Training failed: {res.get('message')}")
    st.stop()

models_dict = comparison.get("models", {})
rankings = comparison.get("rankings", {})

# Metric Ranking Selector
col_sel, col_info = st.columns([1, 2.5])
with col_sel:
    rank_metric = st.selectbox(
        "Rank Models By Primary Metric:",
        options=["f1_score", "roc_auc", "recall", "accuracy", "precision"],
        format_func=lambda x: {
            "f1_score": "F1-Score (Harmonic Balance)",
            "roc_auc": "ROC-AUC (Discriminative Power)",
            "recall": "Recall (Capture Interested Clients)",
            "accuracy": "Accuracy (Overall Correctness)",
            "precision": "Precision (Minimize Wasted Calls)",
        }.get(x, x),
        index=0,
    )

with col_info:
    best_entry = rankings.get(rank_metric, [{}])[0]
    best_model_name = best_entry.get("display_name", "N/A")
    best_score = best_entry.get("value", 0.0)
    st.markdown(
        f"""
        <div style="padding: 10px 14px; background: #eff6ff; border-radius: 8px; border: 1px solid #bfdbfe; font-size: 13px;">
            🏆 <strong>Top Ranked Model ({rank_metric.upper()}):</strong> 
            <span style="font-weight:700; color:#1e3a8a;">{best_model_name}</span> 
            with a score of <strong>{best_score:.2%}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 4 Model Cards Side-by-Side
m_cols = st.columns(4)
model_keys = ["logistic_regression", "decision_tree", "knn", "random_forest"]

for idx, m_key in enumerate(model_keys):
    m_data = models_dict.get(m_key, {})
    m_metrics = m_data.get("metrics", {})
    m_time = m_data.get("timing", {})
    is_best = (m_data.get("display_name") == best_model_name)

    card_class = "model-card model-card-best" if is_best else "model-card"
    best_badge = "<span class='badge badge-success' style='float:right;'>Top Rank</span>" if is_best else ""

    with m_cols[idx]:
        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="model-title">{m_data.get('display_name', m_key)} {best_badge}</div>
                <div style="font-size: 11px; color: #64748b; min-height: 38px; margin-bottom: 12px;">{m_data.get('description', '')}</div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">
                    <span style="color:#64748b;">Accuracy</span>
                    <strong>{m_metrics.get('accuracy', 0):.2%}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">
                    <span style="color:#64748b;">Precision</span>
                    <strong>{m_metrics.get('precision', 0):.2%}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">
                    <span style="color:#64748b;">Recall</span>
                    <strong>{m_metrics.get('recall', 0):.2%}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">
                    <span style="color:#64748b;">F1-Score</span>
                    <strong style="color: #2563eb;">{m_metrics.get('f1_score', 0):.2%}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px;">
                    <span style="color:#64748b;">ROC-AUC</span>
                    <strong style="color: #047857;">{m_metrics.get('roc_auc', 0):.2%}</strong>
                </div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">
                    ⏱ Train: {m_time.get('training_time_sec', 0):.2f}s | Latency: {m_time.get('prediction_time_sec', 0)*1000:.1f}ms
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Detailed Visualizations Tabs
tab_charts, tab_roc, tab_cm, tab_imp, tab_table = st.tabs(
    ["📊 Metric Comparison Chart", "📈 ROC Curves", "🎯 Confusion Matrices", "🌲 Feature Importance", "📋 Metrics Table"]
)

with tab_charts:
    st.markdown("#### Comparative Metric Benchmark")
    fig_bar = render_grouped_metrics_bar(models_dict)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_roc:
    st.markdown("#### Multi-Model Receiver Operating Characteristic (ROC)")
    st.caption("Illustrates the true positive rate versus false positive rate across classification thresholds. Random chance baseline shown as dashed diagonal.")
    fig_roc = render_roc_curves(models_dict)
    st.plotly_chart(fig_roc, use_container_width=True)

with tab_cm:
    st.markdown("#### Confusion Matrices (Held-out Test Subset: 9,043 instances)")
    cm_c1, cm_c2 = st.columns(2)
    with cm_c1:
        st.plotly_chart(
            render_confusion_matrix_heatmap(models_dict["logistic_regression"]["confusion_matrix"], "Logistic Regression"),
            use_container_width=True,
        )
        st.plotly_chart(
            render_confusion_matrix_heatmap(models_dict["knn"]["confusion_matrix"], "KNN"),
            use_container_width=True,
        )
    with cm_c2:
        st.plotly_chart(
            render_confusion_matrix_heatmap(models_dict["decision_tree"]["confusion_matrix"], "Decision Tree"),
            use_container_width=True,
        )
        st.plotly_chart(
            render_confusion_matrix_heatmap(models_dict["random_forest"]["confusion_matrix"], "Random Forest"),
            use_container_width=True,
        )

with tab_imp:
    st.markdown("#### Feature Importance & Statistical Drivers")
    st.caption("Attributes contributing highest information gain (Random Forest / Decision Tree).")
    feat_resp = get_feature_importance()
    if feat_resp and "feature_importance" in feat_resp:
        rf_imp = feat_resp["feature_importance"].get("random_forest", [])
        if rf_imp:
            fig_rf_imp = render_feature_importance_chart(rf_imp, "Random Forest")
            st.plotly_chart(fig_rf_imp, use_container_width=True)
    st.info(feat_resp.get("disclaimer", "Feature importances reflect predictive attribution, not causal proof."))

with tab_table:
    st.markdown("#### Complete Metrics Table")
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
    df_metrics = pd.DataFrame(table_rows)
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

# Precision vs Recall Trade-Off Analysis
st.markdown("---")
st.markdown("#### Analytical Discussion: The Telemarketing Precision-Recall Trade-Off")
st.markdown(
    """
    In retail bank marketing campaigns, classification errors have distinct commercial costs:
    - **False Positives (Type I Error):** Outreach staff call a client who has no interest in opening a term deposit. 
      *Cost:* Operative labor wages, phone telephony toll fees, and customer annoyance.
    - **False Negatives (Type II Error):** The model predicts a client will not subscribe, so no phone call is made—missing an eager depositor. 
      *Cost:* Opportunity loss of substantial long-term deposit capital and interest margin.

    **Why Accuracy is Misleading:**  
    Because 88.3% of contacts do not subscribe, a trivial model predicting 'No' for every customer automatically achieves **88.30% accuracy** 
    while capturing exactly zero subscriptions (Recall = 0%, F1 = 0%). 
    By applying balanced class-weighting, our **Random Forest** and **Decision Tree** models deliberately sacrifice small slices of majority-class accuracy 
    to achieve strong Recall and F1-Scores on the minority target class.
    """
)
