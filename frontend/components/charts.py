import plotly.graph_objects as go
import plotly.express as px
from typing import Any, Dict, List, Optional


def render_target_distribution_chart(target_dist: Dict[str, Any]) -> go.Figure:
    """Renders a polished donut chart for class distribution with center total annotation."""
    no_count = target_dist.get("no", {}).get("count", 39922)
    yes_count = target_dist.get("yes", {}).get("count", 5289)
    total = no_count + yes_count

    labels = [f"No (Non-subscriber) — {no_count:,}", f"Yes (Subscriber) — {yes_count:,}"]
    values = [no_count, yes_count]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                pull=[0, 0.04],
                marker=dict(
                    colors=["#cbd5e1", "#2563eb"],
                    line=dict(color="#ffffff", width=2.5),
                ),
                textinfo="percent",
                hoverinfo="label+percent",
                textposition="inside",
                textfont=dict(size=13, family="Inter", color="#ffffff"),
            )
        ]
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=11, family="Inter", color="#334155"),
        ),
        annotations=[
            dict(
                text=f"<b>{total:,}</b><br><span style='font-size:11px;color:#64748b;'>Total Records</span>",
                x=0.5,
                y=0.5,
                font=dict(size=13, family="Inter", color="#0f172a"),
                showarrow=False,
            )
        ],
        margin=dict(l=15, r=15, t=15, b=35),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_grouped_metrics_bar(models_dict: Dict[str, Any], compact: bool = False) -> go.Figure:
    """
    Renders a clean grouped bar chart comparing Accuracy, Precision, Recall, F1, and ROC-AUC.
    Includes visible top legend, ample headroom, and non-colliding formatted labels.
    If compact=True, formats bar labels with 0-decimals (e.g. 89%) to eliminate horizontal text collisions in side columns.
    """
    metrics_list = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]

    # Professional financial algorithm palette
    model_configs = [
        ("logistic_regression", "Logistic Regression", "#64748b"),
        ("decision_tree", "Decision Tree", "#0284c7"),
        ("knn", "KNN", "#0d9488"),
        ("random_forest", "Random Forest", "#1d4ed8"),
    ]

    fig = go.Figure()

    for model_key, display_label, color in model_configs:
        data = models_dict.get(model_key, {})
        m = data.get("metrics", {})
        scores = [round(m.get(met, 0) * 100, 2) for met in metrics_list]

        if compact:
            bar_text = [f"{s:.0f}%" for s in scores]
            font_size = 9.5
        else:
            bar_text = [f"{s:.1f}%" for s in scores]
            font_size = 10.5

        fig.add_trace(
            go.Bar(
                name=display_label,
                x=metric_labels,
                y=scores,
                marker=dict(
                    color=color,
                    line=dict(color="#ffffff", width=1),
                ),
                text=bar_text,
                textposition="outside",
                textfont=dict(size=font_size, family="Inter", color="#1e293b"),
                cliponaxis=False,
                hovertemplate=f"<b>{display_label}</b><br>%{{x}}: <b>%{{y:.2f}}%</b><extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        bargap=0.20 if compact else 0.24,
        bargroupgap=0.04 if compact else 0.08,
        yaxis=dict(
            title=dict(text="Performance Score (%)", font=dict(size=12, family="Inter", color="#334155")),
            range=[0, 114],
            gridcolor="#f1f5f9",
            zeroline=False,
            tickfont=dict(size=11, family="Inter", color="#64748b"),
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=12, family="Inter", color="#0f172a"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(size=11, family="Inter", color="#1e293b"),
        ),
        margin=dict(l=20 if compact else 25, r=15 if compact else 20, t=55, b=25),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_roc_curves(models_dict: Dict[str, Any]) -> go.Figure:
    """Renders comparative ROC curves across all four algorithms with shaded area for best model."""
    fig = go.Figure()

    model_colors = {
        "random_forest": "#1d4ed8",
        "logistic_regression": "#64748b",
        "knn": "#10b981",
        "decision_tree": "#0284c7",
    }

    # Diagonal baseline (random guess)
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line=dict(color="#cbd5e1", dash="dash", width=1.5),
            name="Random Guess (AUC = 0.50)",
        )
    )

    for model_key in ["random_forest", "logistic_regression", "knn", "decision_tree"]:
        data = models_dict.get(model_key, {})
        roc_data = data.get("curves", {}).get("roc", {})
        fpr = roc_data.get("fpr", [])
        tpr = roc_data.get("tpr", [])
        auc = data.get("metrics", {}).get("roc_auc")
        auc_str = f"{auc:.3f}" if auc else "N/A"
        name = data.get("display_name", model_key).replace(" Classifier", "").replace(" (KNN)", "")

        if fpr and tpr:
            # Highlight Random Forest with subtle area fill
            fill_arg = "tozeroy" if model_key == "random_forest" else "none"
            fill_color = "rgba(29, 78, 216, 0.05)" if model_key == "random_forest" else None

            fig.add_trace(
                go.Scatter(
                    x=fpr,
                    y=tpr,
                    mode="lines",
                    name=f"{name} (AUC: {auc_str})",
                    line=dict(color=model_colors.get(model_key, "#2563eb"), width=2.5 if model_key == "random_forest" else 2),
                    fill=fill_arg,
                    fillcolor=fill_color,
                )
            )

    fig.update_layout(
        xaxis=dict(
            title=dict(text="False Positive Rate (1 - Specificity)", font=dict(size=12, family="Inter", color="#334155")),
            gridcolor="#f1f5f9",
            range=[0, 1],
            tickfont=dict(size=11, family="Inter", color="#64748b"),
        ),
        yaxis=dict(
            title=dict(text="True Positive Rate (Sensitivity / Recall)", font=dict(size=12, family="Inter", color="#334155")),
            gridcolor="#f1f5f9",
            range=[0, 1.02],
            tickfont=dict(size=11, family="Inter", color="#64748b"),
        ),
        legend=dict(
            yanchor="bottom",
            y=0.04,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255, 255, 255, 0.92)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(size=11, family="Inter", color="#1e293b"),
        ),
        margin=dict(l=25, r=20, t=25, b=25),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_confusion_matrix_heatmap(cm_dict: Dict[str, Any], model_name: str) -> go.Figure:
    """Renders a clean annotated confusion matrix heatmap with crisp cell contrast."""
    tn = cm_dict.get("true_negatives", 0)
    fp = cm_dict.get("false_positives", 0)
    fn = cm_dict.get("false_negatives", 0)
    tp = cm_dict.get("true_positives", 0)

    z = [[tn, fp], [fn, tp]]
    total = max(tn + fp + fn + tp, 1)

    text = [
        [f"<b>TN: {tn:,}</b><br><span style='font-size:11px;'>({tn/total:.1%})</span>", f"<b>FP: {fp:,}</b><br><span style='font-size:11px;'>({fp/total:.1%})</span>"],
        [f"<b>FN: {fn:,}</b><br><span style='font-size:11px;'>({fn/total:.1%})</span>", f"<b>TP: {tp:,}</b><br><span style='font-size:11px;'>({tp/total:.1%})</span>"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=["Predicted: No", "Predicted: Yes"],
            y=["Actual: No", "Actual: Yes"],
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=13, family="Inter", color="#0f172a"),
            colorscale=[[0, "#f8fafc"], [0.2, "#e0f2fe"], [1, "#93c5fd"]],
            showscale=False,
            xgap=4,
            ygap=4,
        )
    )

    clean_name = model_name.replace(" Classifier", "").replace(" (KNN)", "")

    fig.update_layout(
        margin=dict(l=35, r=35, t=35, b=35),
        height=260,
        title=dict(
            text=f"Confusion Matrix: {clean_name}",
            font=dict(size=13.5, family="Inter", color="#0f172a"),
            x=0.5,
            xanchor="center",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(size=11, family="Inter", color="#334155")),
        yaxis=dict(tickfont=dict(size=11, family="Inter", color="#334155")),
    )
    return fig


FEATURE_NAME_MAP = {
    "age": "Client Age",
    "balance": "Account Balance (EUR)",
    "day": "Day of Month Contacted",
    "campaign": "Campaign Contacts Count",
    "pdays": "Days Since Prior Campaign",
    "previous": "Previous Contacts Count",
    "poutcome_success": "Prior Outcome: Success",
    "poutcome_failure": "Prior Outcome: Failure",
    "poutcome_other": "Prior Outcome: Other",
    "poutcome_unknown": "Prior Outcome: Unknown / First-time",
    "housing_yes": "Housing Loan: Yes",
    "housing_no": "Housing Loan: No",
    "loan_yes": "Personal Loan: Yes",
    "loan_no": "Personal Loan: No",
    "contact_cellular": "Contact: Cellular",
    "contact_telephone": "Contact: Landline",
    "contact_unknown": "Contact: Unknown Channel",
    "marital_married": "Marital: Married",
    "marital_single": "Marital: Single",
    "marital_divorced": "Marital: Divorced",
    "education_tertiary": "Education: Tertiary Degree",
    "education_secondary": "Education: Secondary School",
    "education_primary": "Education: Primary School",
    "default_yes": "Credit Default: Yes",
    "default_no": "Credit Default: No",
}


def render_feature_importance_chart(importance_list: List[Dict[str, Any]], model_name: str) -> go.Figure:
    """Renders horizontal bar chart of top predictive features with gradient ranking and clean labels."""
    if not importance_list:
        return go.Figure()

    df_imp = sorted(importance_list[:10], key=lambda x: x["importance"])
    raw_features = [item["feature"] for item in df_imp]
    scores = [item["importance"] for item in df_imp]

    # Map raw technical strings into executive banking terms
    clean_features = [
        FEATURE_NAME_MAP.get(f, f.replace("_", " ").title())
        for f in raw_features
    ]

    # Highlight top feature with deep royal blue, others with sleek cobalt
    colors = ["#1d4ed8" if i == len(scores) - 1 else "#3b82f6" for i in range(len(scores))]

    fig = go.Figure(
        go.Bar(
            x=scores,
            y=clean_features,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="#ffffff", width=1),
            ),
            text=[f"{s:.3f}" for s in scores],
            textposition="outside",
            textfont=dict(size=10.5, family="Inter", color="#1e293b"),
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Importance Weight: <b>%{x:.4f}</b><extra></extra>",
        )
    )

    clean_name = model_name.replace(" Classifier", "").replace(" (KNN)", "")

    fig.update_layout(
        title=dict(
            text=f"Top 10 Feature Importance Weights — {clean_name}",
            font=dict(size=13.5, family="Inter", color="#0f172a"),
            x=0.02,
        ),
        xaxis=dict(
            title=dict(text="Gini Importance Score (Relative Weight)", font=dict(size=11.5, family="Inter", color="#334155")),
            gridcolor="#f1f5f9",
            tickfont=dict(size=11, family="Inter", color="#64748b"),
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=11.5, family="Inter", color="#0f172a"),
        ),
        margin=dict(l=195, r=45, t=40, b=25),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_prediction_gauge(probability: float, title_text: str = "Subscription Probability") -> go.Figure:
    """Renders an interactive gauge displaying customer conversion probability with high-contrast text."""
    pct = probability * 100

    bar_color = "#16a34a" if pct >= 60 else ("#d97706" if pct >= 40 else "#dc2626")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 32, "color": "#0f172a", "family": "Inter"}},
            title={"text": title_text, "font": {"size": 13.5, "color": "#475569", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8", "tickfont": {"size": 10, "color": "#64748b"}},
                "bar": {"color": bar_color, "thickness": 0.35},
                "bgcolor": "#f8fafc",
                "borderwidth": 1,
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0, 40], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [40, 60], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [60, 100], "color": "rgba(34, 197, 94, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#dc2626", "width": 3},
                    "thickness": 0.75,
                    "value": 50,
                },
            },
        )
    )

    fig.update_layout(
        margin=dict(l=25, r=25, t=35, b=25),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_customer_all_models_probability_bar(models_dict: Dict[str, Any]) -> go.Figure:
    """
    Renders a bar chart comparing this specific customer's predicted subscription probability
    across all four trained models, with a 50% decision threshold indicator.
    """
    model_names = []
    probabilities = []
    colors_list = []
    hover_texts = []

    for key in ["random_forest", "decision_tree", "logistic_regression", "knn"]:
        m_data = models_dict.get(key, {})
        name = m_data.get("model_name", key)
        prob = m_data.get("probability_percentage", (m_data.get("probability", 0) or 0) * 100)
        acc = m_data.get("benchmark_accuracy")
        acc_str = f"{acc:.2%}" if acc else "N/A"
        pred = m_data.get("outcome", "No")

        clean_label = name.replace(" Classifier", "").replace(" (KNN)", "")
        model_names.append(clean_label)
        probabilities.append(round(prob, 1))
        # Green if >= 50% conversion probability, else Blue
        colors_list.append("#16a34a" if prob >= 50 else "#2563eb")
        hover_texts.append(
            f"<b>{name}</b><br>"
            f"Predicted: {pred}<br>"
            f"Probability: {prob:.1f}%<br>"
            f"Model Benchmark Accuracy: {acc_str}"
        )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=model_names,
            y=probabilities,
            marker=dict(
                color=colors_list,
                line=dict(color="#ffffff", width=1.5),
            ),
            text=[f"{p:.1f}%" for p in probabilities],
            textposition="outside",
            textfont=dict(size=11, family="Inter", color="#0f172a"),
            hoverinfo="text",
            hovertext=hover_texts,
            width=0.45,
            cliponaxis=False,
        )
    )

    # 50% classification threshold line
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="#dc2626",
        annotation_text="Decision Threshold (50%)",
        annotation_position="top right",
        annotation_font_color="#dc2626",
        annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(
            text="Customer Subscription Propensity Across All 4 Supervised Models",
            font=dict(size=13.5, family="Inter", color="#0f172a"),
            x=0.02,
        ),
        yaxis=dict(
            title=dict(text="Predicted Probability (%)", font=dict(size=12, family="Inter", color="#334155")),
            range=[0, 110],
            gridcolor="#f1f5f9",
            tickfont=dict(size=11, family="Inter", color="#64748b"),
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=12, family="Inter", color="#0f172a"),
        ),
        margin=dict(l=25, r=25, t=45, b=25),
        height=330,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_model_accuracy_vs_probability_bar(models_dict: Dict[str, Any]) -> go.Figure:
    """
    Renders a grouped bar chart comparing each model's Benchmark Accuracy against
    this specific customer's predicted subscription probability.
    """
    model_names = []
    accuracies = []
    probabilities = []

    for key in ["random_forest", "decision_tree", "logistic_regression", "knn"]:
        m_data = models_dict.get(key, {})
        name = m_data.get("model_name", key).replace(" Classifier", "").replace(" (KNN)", "")
        prob = m_data.get("probability_percentage", (m_data.get("probability", 0) or 0) * 100)
        acc = (m_data.get("benchmark_accuracy") or 0) * 100

        model_names.append(name)
        accuracies.append(round(acc, 1))
        probabilities.append(round(prob, 1))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Model Benchmark Accuracy",
            x=model_names,
            y=accuracies,
            marker_color="#1d4ed8",
            text=[f"{a:.1f}%" for a in accuracies],
            textposition="outside",
            textfont=dict(size=10, family="Inter", color="#334155"),
            cliponaxis=False,
        )
    )

    fig.add_trace(
        go.Bar(
            name="This Customer's Propensity",
            x=model_names,
            y=probabilities,
            marker_color="#0284c7",
            text=[f"{p:.1f}%" for p in probabilities],
            textposition="outside",
            textfont=dict(size=10, family="Inter", color="#334155"),
            cliponaxis=False,
        )
    )

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
        title=dict(
            text="Model Benchmark Test Accuracy vs. Customer Propensity",
            font=dict(size=13.5, family="Inter", color="#0f172a"),
            x=0.02,
        ),
        yaxis=dict(
            title=dict(text="Percentage (%)", font=dict(size=12, family="Inter", color="#334155")),
            range=[0, 110],
            gridcolor="#f1f5f9",
            tickfont=dict(size=11, family="Inter", color="#64748b"),
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=12, family="Inter", color="#0f172a"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(size=11, family="Inter", color="#1e293b"),
        ),
        margin=dict(l=25, r=25, t=55, b=25),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
