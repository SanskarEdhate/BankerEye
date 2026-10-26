import sys
import time
import textwrap
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
    get_training_status,
    clear_all_api_caches,
)
from frontend.components.charts import (
    render_grouped_metrics_bar,
    render_roc_curves,
    render_confusion_matrix_heatmap,
    render_feature_importance_chart,
)

st.markdown(
    """
    <div class="bank-header">
        <h1>Empirical Model Comparison & Benchmarking</h1>
        <p>Comprehensive Evaluation of 4 Supervised Algorithms on Held-Out Test Data</p>
    </div>
    """,
    unsafe_allow_html=True,
)

health = check_api_health()
if health.get("status") != "healthy":
    st.error("⚠️ Flask API is offline. Start the backend with: `python backend/app.py`")
    st.stop()

comparison = get_model_comparison()
models_ready = comparison and comparison.get("status") == "ready" and bool(comparison.get("models"))

if not models_ready:
    st.info("Models have not been trained yet. Click below to train Logistic Regression, Decision Tree, KNN, and Random Forest.")
    if st.button("🚀 Train All 4 Models", type="primary", width="stretch"):
        resp = trigger_model_training()
        if resp.get("status") in ("training_started", "busy"):
            progress_bar = st.progress(0)
            status_container = st.empty()
            status_container.info("Training background job started. Evaluating 4 algorithms...")

            done = False
            while not done:
                time.sleep(1.2)
                st_info = get_training_status()
                curr_state = st_info.get("state", "unknown")
                curr_prog = int(st_info.get("progress", 0))
                progress_bar.progress(min(curr_prog, 100))
                status_container.info(f"Training in progress ({curr_prog}%): {st_info.get('message', 'Computing...')}")

                if curr_state == "done":
                    clear_all_api_caches()
                    progress_bar.progress(100)
                    status_container.success("Models successfully trained! Refreshing page...")
                    time.sleep(1)
                    st.rerun()
                    done = True
                elif curr_state == "failed":
                    status_container.error(f"Training failed: {st_info.get('error', 'Unknown error')}")
                    done = True
        else:
            st.error(f"Training failed: {resp.get('message')}")
    st.stop()

models_dict = comparison.get("models", {})
rankings = comparison.get("rankings", {})
split_info = comparison.get("split_info", {})
test_target_dist = split_info.get("test_target_distribution", {})
yes_pct = test_target_dist.get("yes_pct", 11.7)
no_pct = round(100.0 - yes_pct, 1)
test_rows = split_info.get("test_rows", 0)

# Statistical Distinguishability Banner
verdict_text = comparison.get("statistical_verdict")
if verdict_text:
    is_distinguishable = comparison.get("is_top_model_distinguishable", True)
    banner_bg = "#eff6ff" if is_distinguishable else "#fffbeb"
    banner_border = "#bfdbfe" if is_distinguishable else "#fde68a"
    banner_icon = "📊" if is_distinguishable else "⚠️"
    st.markdown(
        f"""
        <div style="padding: 12px 16px; background: {banner_bg}; border-radius: 8px; border: 1px solid {banner_border}; font-size: 13.5px; margin-bottom: 14px; color: #1e293b;">
            {banner_icon} <strong>Statistical Significance Notice:</strong> {verdict_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# Metric Ranking Selector
col_sel, col_info = st.columns([1.3, 2.0])
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
        <div style="padding: 10px 14px; background: #eff6ff; border-radius: 8px; border: 1px solid #bfdbfe; font-size: 13px; margin-top: 24px;">
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
    best_badge = "<span class='badge badge-success'>Top Rank</span>" if is_best else ""

    with m_cols[idx]:
        card_content = (
            f'<div class="{card_class}">'
            f'<div class="model-header">'
            f'<span class="model-title">{m_data.get("display_name", m_key)}</span>'
            f'{best_badge}'
            f'</div>'
            f'<div style="font-size: 11px; color: #64748b; min-height: 38px; margin-bottom: 12px; line-height: 1.35;">{m_data.get("description", "")}</div>'
            f'<div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">'
            f'<span style="color:#64748b;">Accuracy</span>'
            f'<strong>{m_metrics.get("accuracy", 0):.2%}</strong>'
            f'</div>'
            f'<div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">'
            f'<span style="color:#64748b;">Precision</span>'
            f'<strong>{m_metrics.get("precision", 0):.2%}</strong>'
            f'</div>'
            f'<div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">'
            f'<span style="color:#64748b;">Recall</span>'
            f'<strong>{m_metrics.get("recall", 0):.2%}</strong>'
            f'</div>'
            f'<div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0; font-size: 13px;">'
            f'<span style="color:#64748b;">F1-Score</span>'
            f'<strong style="color: #2563eb;">{m_metrics.get("f1_score", 0):.2%}</strong>'
            f'</div>'
            f'<div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px;">'
            f'<span style="color:#64748b;">ROC-AUC</span>'
            f'<strong style="color: #047857;">{m_metrics.get("roc_auc", 0):.2%}</strong>'
            f'</div>'
            f'<div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">'
            f'⏱ Train: {m_time.get("training_time_sec", 0):.2f}s | Latency: {m_time.get("prediction_time_sec", 0)*1000:.1f}ms'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_content, unsafe_allow_html=True)

# Detailed Visualizations Tabs
tab_charts, tab_roc, tab_cm, tab_imp, tab_ci, tab_temporal, tab_table = st.tabs(
    [
        "📊 Metric Comparison Chart",
        "📈 ROC Curves",
        "🎯 Confusion Matrices",
        "🌲 Feature Importance",
        "🔬 95% Confidence Intervals",
        "⏱ Temporal Sensitivity Check",
        "📋 Full Metrics Table",
    ]
)

with tab_charts:
    st.markdown("#### Comparative Metric Benchmark")
    fig_bar = render_grouped_metrics_bar(models_dict)
    st.plotly_chart(fig_bar, width="stretch")

with tab_roc:
    st.markdown("#### Multi-Model Receiver Operating Characteristic (ROC)")
    st.caption("Illustrates true positive rate vs false positive rate across thresholds with boundary preservation (starts at 0.0, ends at 1.0).")
    fig_roc = render_roc_curves(models_dict)
    st.plotly_chart(fig_roc, width="stretch")

with tab_cm:
    st.markdown(f"#### Confusion Matrices (Held-out Test Subset: {test_rows:,} instances)")
    cm_c1, cm_c2 = st.columns(2)
    with cm_c1:
        if "logistic_regression" in models_dict and "confusion_matrix" in models_dict["logistic_regression"]:
            st.plotly_chart(
                render_confusion_matrix_heatmap(models_dict["logistic_regression"]["confusion_matrix"], "Logistic Regression"),
                width="stretch",
            )
        if "knn" in models_dict and "confusion_matrix" in models_dict["knn"]:
            st.plotly_chart(
                render_confusion_matrix_heatmap(models_dict["knn"]["confusion_matrix"], "KNN"),
                width="stretch",
            )
    with cm_c2:
        if "decision_tree" in models_dict and "confusion_matrix" in models_dict["decision_tree"]:
            st.plotly_chart(
                render_confusion_matrix_heatmap(models_dict["decision_tree"]["confusion_matrix"], "Decision Tree"),
                width="stretch",
            )
        if "random_forest" in models_dict and "confusion_matrix" in models_dict["random_forest"]:
            st.plotly_chart(
                render_confusion_matrix_heatmap(models_dict["random_forest"]["confusion_matrix"], "Random Forest"),
                width="stretch",
            )

with tab_imp:
    st.markdown("#### Grouped Permutation Feature Importance")
    st.caption("Permutation importance computed on the held-out test set with one-hot encoded columns grouped back to original attributes.")
    feat_resp = get_feature_importance()
    if feat_resp and isinstance(feat_resp, dict) and "feature_importance" in feat_resp:
        rf_imp = feat_resp["feature_importance"].get("random_forest", [])
        if rf_imp:
            fig_rf_imp = render_feature_importance_chart(rf_imp, "Random Forest")
            st.plotly_chart(fig_rf_imp, width="stretch")
        disclaimer = feat_resp.get("disclaimer", "Feature importances reflect predictive correlation, not causal proof.")
        st.info(disclaimer)
    else:
        st.warning("Feature importance data is currently not available.")

with tab_ci:
    st.markdown("#### Bootstrap 95% Confidence Intervals & Probabilistic Calibration")
    st.caption("Non-parametric percentile bootstrap (n=500 resamples) on test data and isotonic probability calibration (cv=3).")

    ci_rows = []
    for k in model_keys:
        d = models_dict.get(k, {})
        m = d.get("metrics", {})
        ci = d.get("bootstrap_ci_95", {})
        cal = d.get("calibration", {})
        opt_th = d.get("optimal_threshold", 0.50)
        hp = d.get("hyperparameters", {})

        f1_ci = ci.get("f1_ci_95", [None, None])
        roc_ci = ci.get("roc_auc_ci_95", [None, None])
        cv_f1 = hp.get("cv_mean_f1")
        cv_std = hp.get("cv_std_f1")

        ci_rows.append({
            "Algorithm": d.get("display_name", k),
            "Test F1-Score": f"{m.get('f1_score', 0):.2%}",
            "F1 95% Bootstrap CI": f"[{f1_ci[0]:.4f}, {f1_ci[1]:.4f}]" if f1_ci[0] is not None else "N/A",
            "Test ROC-AUC": f"{m.get('roc_auc', 0):.2%}" if m.get("roc_auc") else "N/A",
            "ROC-AUC 95% CI": f"[{roc_ci[0]:.4f}, {roc_ci[1]:.4f}]" if roc_ci[0] is not None else "N/A",
            "Brier Score (Calibrated)": f"{cal.get('brier_score', m.get('brier_score', 0)):.4f}",
            "Optimal Threshold": f"{opt_th:.2f}",
            "5-Fold CV F1 (Train)": f"{cv_f1:.4f} ± {cv_std:.4f}" if cv_f1 is not None else "N/A",
        })

    st.dataframe(pd.DataFrame(ci_rows), width="stretch", hide_index=True)
    st.info("ℹ️ Note on Statistical Distinguishability: When the 95% confidence intervals of two top-performing models overlap, "
            "their test performances are not statistically distinguishable, and neither can be definitively claimed as superior.")

with tab_temporal:
    st.markdown("#### Time-Aware Sensitivity Check (Secondary Benchmark)")
    st.caption("Evaluates models on a chronological split holding out the last 20% of records in file order without shuffling, testing sensitivity to non-stationary sequence drift.")

    temporal_data = comparison.get("temporal_check", {})
    t_models = temporal_data.get("models", {})

    if t_models:
        temp_rows = []
        for k in model_keys:
            tm = t_models.get(k, {})
            temp_rows.append({
                "Algorithm": tm.get("display_name", k),
                "Temporal Accuracy": f"{tm.get('accuracy', 0):.2%}",
                "Temporal Precision": f"{tm.get('precision', 0):.2%}",
                "Temporal Recall": f"{tm.get('recall', 0):.2%}",
                "Temporal F1-Score": f"{tm.get('f1_score', 0):.2%}",
                "Temporal ROC-AUC": f"{tm.get('roc_auc', 0):.2%}" if tm.get("roc_auc") else "N/A",
                "Temporal Brier Score": f"{tm.get('brier_score', 0):.4f}",
            })
        st.dataframe(pd.DataFrame(temp_rows), width="stretch", hide_index=True)
        st.warning("⚠️ Sensitivity Check Notice: This temporal partition serves as a sensitivity stress-test. "
                   "Because records in the bank telemarketing campaign reflect time-ordered market interest, "
                   "the stratified random split remains the primary operational benchmark.")
    else:
        st.info("Temporal sensitivity check results are not available.")

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
    st.dataframe(df_metrics, width="stretch", hide_index=True)

# Precision vs Recall Trade-Off Analysis
st.markdown("---")
st.markdown("#### Analytical Discussion: The Telemarketing Precision-Recall Trade-Off")
st.markdown(
    f"""
    In retail bank marketing campaigns, classification errors have distinct commercial costs:
    - **False Positives (Type I Error):** Outreach staff call a client who has no interest in opening a term deposit. 
      *Cost:* Operative labor wages, phone telephony toll fees, and customer annoyance.
    - **False Negatives (Type II Error):** The model predicts a client will not subscribe, so no phone call is made—missing an eager depositor. 
      *Cost:* Opportunity loss of substantial long-term deposit capital and interest margin.

    **Why Accuracy is Misleading:**  
    Because {no_pct:.1f}% of contacts do not subscribe, a trivial model predicting 'No' for every customer automatically achieves **{no_pct:.2f}% accuracy** 
    while capturing exactly zero subscriptions (Recall = 0%, F1 = 0%). 
    By applying balanced class-weighting, our **Random Forest** and **Decision Tree** models deliberately trade off small slices of majority-class accuracy 
    to achieve strong Recall and F1-Scores on the minority target class.
    """
)
