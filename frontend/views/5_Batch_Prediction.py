import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import (
    check_api_health,
    predict_batch_csv,
    get_dataset_sample,
)
from frontend.components.cards import render_kpi_card, render_info_banner

st.markdown(
    """
    <div class="bank-header">
        <h1>Batch Customer Campaign Scoring</h1>
        <p>High-Throughput CSV Batch Inference, Conversion Summaries, and Exportable Predictions</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Health Check
health = check_api_health()
if health.get("status") != "healthy":
    st.error("⚠️ Flask API is offline. Start the backend with: `python backend/app.py`")
    st.stop()

if not health.get("models_trained"):
    st.warning("⚠️ Machine learning models have not been trained yet. Please train them first via the Dashboard.")
    st.stop()

render_info_banner(
    "Upload Requirements: The uploaded CSV must contain the standard customer features: age, job, marital, education, "
    "default, balance, housing, loan, contact, day, month, campaign, pdays, previous, and poutcome. "
    "If 'duration' or 'y' are present in the uploaded file, they are automatically ignored during inference.",
    title="Batch CSV Format"
)

# Downloadable Sample Template
col_up, col_template = st.columns([2.5, 1])

with col_template:
    st.markdown("##### Need a Test CSV?")
    st.caption("first 25 rows of the dataset")
    sample_records = get_dataset_sample(limit=25)
    if sample_records:
        df_sample_template = pd.DataFrame(sample_records)
        # Drop y and duration to make a clean pre-campaign template
        cols_to_keep = [c for c in df_sample_template.columns if c not in ["y", "duration"]]
        template_csv = df_sample_template[cols_to_keep].to_csv(index=False)
        st.download_button(
            label="📥 Download Sample Batch Template (CSV)",
            data=template_csv,
            file_name="sample_batch_customers.csv",
            mime="text/csv",
            width="stretch",
        )

with col_up:
    uploaded_file = st.file_uploader("Upload Customer CSV File:", type=["csv"])
    model_choice = st.selectbox(
        "Select Scoring Algorithm:",
        options=["random_forest", "decision_tree", "logistic_regression", "knn"],
        format_func=lambda x: {
            "random_forest": "Random Forest Classifier (Ensemble)",
            "decision_tree": "Decision Tree Classifier",
            "logistic_regression": "Logistic Regression",
            "knn": "K-Nearest Neighbours (KNN)",
        }.get(x, x),
        index=0,
    )

if uploaded_file is not None:
    try:
        # Detect delimiter or standard comma
        df_upload = pd.read_csv(uploaded_file, sep=None, engine="python")
        st.markdown("#### Uploaded File Preview")
        st.caption(f"Loaded {len(df_upload)} rows and {len(df_upload.columns)} columns.")
        st.dataframe(df_upload.head(10), width="stretch", height=220)

        # Execute Batch Prediction
        if st.button("🚀 Run Batch Prediction", type="primary", width="stretch"):
            with st.spinner("Processing batch records through the trained pipeline..."):
                resp = predict_batch_csv(df=df_upload, model_name=model_choice)

            if resp.get("status") == "success":
                st.success("Batch prediction completed successfully!")

                # Summary KPIs
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    render_kpi_card("Total Scored", f"{resp.get('total_records', 0):,}", "Batch input size", "Processed", "info")
                with k2:
                    render_kpi_card("Predicted Subscribers", f"{resp.get('predicted_positive', 0):,}", "Class = Yes", "Target Leads", "success")
                with k3:
                    render_kpi_card("Predicted Non-Subscribers", f"{resp.get('predicted_negative', 0):,}", "Class = No", "Excluded", "warning")
                with k4:
                    render_kpi_card("Conversion Propensity", f"{resp.get('positive_rate_percentage', 0):.1f}%", "Outreach efficiency", "Yield", "info")

                # Breakdown Chart
                st.markdown("#### Propensity Distribution")
                pos_n = resp.get("predicted_positive", 0)
                neg_n = resp.get("predicted_negative", 0)
                tot_n = pos_n + neg_n

                fig_batch_pie = go.Figure(
                    data=[
                        go.Pie(
                            labels=[f"Subscribers (Yes) — {pos_n:,}", f"Non-Subscribers (No) — {neg_n:,}"],
                            values=[pos_n, neg_n],
                            hole=0.58,
                            pull=[0.05, 0],
                            marker=dict(
                                colors=["#16a34a", "#cbd5e1"],
                                line=dict(color="#ffffff", width=2),
                            ),
                            textinfo="percent",
                            hoverinfo="label+percent",
                            textposition="inside",
                            textfont=dict(size=12.5, family="Inter", color="#ffffff"),
                        )
                    ]
                )
                fig_batch_pie.update_layout(
                    height=300,
                    annotations=[
                        dict(
                            text=f"<b>{tot_n:,}</b><br><span style='font-size:11px;color:#64748b;'>Total Scored</span>",
                            x=0.5,
                            y=0.5,
                            font=dict(size=13, family="Inter", color="#0f172a"),
                            showarrow=False,
                        )
                    ],
                    margin=dict(t=20, b=25, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=11, family="Inter", color="#334155"),
                    ),
                )
                st.plotly_chart(fig_batch_pie, width="stretch")

                # Attach predictions to original dataframe
                results_data = resp.get("results", [])
                df_results = df_upload.copy()
                df_results["predicted_subscription"] = [r["outcome"] for r in results_data]
                df_results["subscription_probability"] = [r["probability"] for r in results_data]

                st.markdown("#### Detailed Prediction Results Table")
                st.dataframe(df_results, width="stretch", height=350)

                # Downloadable Results CSV
                results_csv = df_results.to_csv(index=False)
                st.download_button(
                    label="📥 Download Scored Batch Results (CSV)",
                    data=results_csv,
                    file_name=f"scored_customers_{model_choice}.csv",
                    mime="text/csv",
                    type="primary",
                )
            else:
                st.error(f"Batch prediction error: {resp.get('message', 'Validation error')}")
                val_errors = resp.get("validation_errors", [])
                if val_errors:
                    st.markdown(f"##### ⚠️ Per-Row Validation Errors ({len(val_errors)} detected)")
                    df_errors = pd.DataFrame(val_errors)
                    st.dataframe(df_errors, width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"Error parsing uploaded file: {e}")
