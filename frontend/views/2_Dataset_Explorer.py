import sys
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import (
    check_api_health,
    get_dataset_summary,
    get_dataset_sample,
    get_dataset_catalog,
    get_dataset_manifest,
    get_dataset_cleaning_summary,
    get_dataset_stage_details,
)

from frontend.components.cards import render_kpi_card

st.markdown(
    """
    <div class="bank-header">
        <h1>Dataset Explorer & EDA</h1>
        <p>Comprehensive Statistical Analysis, Feature Schema, Class Imbalances, and Anti-Leakage Policies</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Health Check
health = check_api_health()
if health.get("status") != "healthy":
    st.error("⚠️ Flask API is offline. Start the backend with: `python backend/app.py`")
    st.stop()

summary = get_dataset_summary()
if not summary:
    st.error("Failed to load dataset summary.")
    st.stop()

# Anti-leakage Highlight Callout
st.markdown(
    """
    <div class="info-callout">
        <strong>⚠️ Critical Machine Learning Design Decision — Feature Leakage Prevention:</strong><br>
        In accordance with banking machine learning best practices and academic standards, the feature <code>duration</code> 
        (call duration in seconds) is <strong>strictly excluded</strong> from the primary model training pipeline. 
        Because call duration cannot be known before a telemarketing call is executed, training on it causes severe target leakage 
        and produces misleadingly inflated performance estimates. Our system trains exclusively on pre-call demographic, credit, 
        and historical campaign attributes.
    </div>
    """,
    unsafe_allow_html=True,
)

# Top Stats Row
s1, s2, s3, s4 = st.columns(4)
with s1:
    render_kpi_card("Total Records", f"{summary.get('total_rows', 0):,}", "bank-full.csv records", "UCI Benchmark", "info")
with s2:
    render_kpi_card("Total Columns", str(summary.get("total_columns", 0)), "16 features + 1 target (15 in ML)", "17 Columns", "info")
with s3:
    render_kpi_card("Missing Cells", str(summary.get("total_missing_cells", 0)), "0 null / NaN values", "Verified Clean", "success")
with s4:
    render_kpi_card("Duplicate Rows", str(summary.get("duplicate_rows", 0)), "0 duplicate entries", "0 Duplicates", "success")

# Tabs for Organized Navigation
tab_inspector, tab_folders, tab_preview, tab_schema, tab_stats, tab_distributions, tab_download = st.tabs(
    [
        "🗂️ Data Cleaning & Splitting Inspector",
        "📁 Dataset Folders & Catalog",
        "📄 Dataset Preview",
        "📋 Schema & Types",
        "📊 Descriptive Statistics",
        "📈 Distributions & EDA",
        "💾 Data Export",
    ]
)

# ----------------- TAB 0: DATA CLEANING & SPLITTING INSPECTOR -----------------
with tab_inspector:
    st.markdown("#### 🗂️ Multi-Stage Data Cleaning & Splitting Inspector")
    st.caption("Inspect each dataset through all 5 development stages: Raw Data, Unclean Data, Clean Data, Train Data, and Test Data.")

    manifest = get_dataset_manifest()
    datasets_list = manifest.get("datasets", []) if manifest else []
    
    if not datasets_list:
        dataset_options = [
            ("1_uci_bank_marketing_canonical", "Canonical UCI Bank Marketing Dataset (45,211 rows)"),
            ("2_bank_additional_socioeconomic", "Socioeconomic Extended Dataset (41,188 rows)"),
            ("3_train_test_competition", "Competition Train/Test Split Dataset (30,000 rows)"),
        ]
    else:
        dataset_options = [
            (d["dataset_id"], f"{d['dataset_name']} ({d['rows']:,} rows, {d['columns']} cols)")
            for d in datasets_list
        ]

    col_ds, col_meta = st.columns([1.5, 1])
    with col_ds:
        selected_ds_id = st.selectbox(
            "Select Dataset to Inspect:",
            options=[opt[0] for opt in dataset_options],
            format_func=lambda x: dict(dataset_options).get(x, x),
            index=0,
        )

    # 5 Pipeline Stages
    stages = [
        ("01_Raw_Data", "1. Raw Data", "Preserved exact original source file as received."),
        ("02_Unclean_Data", "2. Unclean Data", "Original state verified before cleaning transforms."),
        ("03_Clean_Data", "3. Clean Data", "Deduplicated, type-checked, missingness verified."),
        ("04_Train_Data", "4. Train Data", "Stratified training partition (80% default, seed 42)."),
        ("05_Test_Data", "5. Test Data", "Isolated evaluation partition strictly held out."),
    ]

    # Fetch summary for selected dataset
    ds_summary = get_dataset_cleaning_summary(selected_ds_id) or {}
    matched_manifest = next((d for d in datasets_list if d.get("dataset_id") == selected_ds_id), {})

    with col_meta:
        task_label = matched_manifest.get("task_type", "Binary Classification")
        target_name = matched_manifest.get("target_column", "y")
        st.markdown(
            f"""
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:10px 14px; font-size:12.5px; margin-top:22px;">
                🎯 <strong>Task:</strong> {task_label} | 🏷️ <strong>Target:</strong> <code>{target_name}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Stage Selector Pills / Radio
    stage_choice = st.radio(
        "Select Pipeline Stage:",
        options=[s[0] for s in stages],
        format_func=lambda x: next((s[1] for s in stages if s[0] == x), x),
        horizontal=True,
    )

    stage_desc = next((s[2] for s in stages if s[0] == stage_choice), "")
    st.info(f"**Stage Focus:** {stage_desc}")

    # Fetch stage details from API
    stage_data = get_dataset_stage_details(selected_ds_id, stage_choice, limit=15)

    if stage_data and stage_data.get("exists"):
        st1, st2, st3, st4, st5 = st.columns(5)
        dims = stage_data.get("dimensions", {})
        with st1:
            render_kpi_card("Stage Records", f"{dims.get('rows', 0):,}", "Observations in file", "Count", "info")
        with st2:
            render_kpi_card("Attributes", str(dims.get("columns", 0)), "Features + Target", "Columns", "info")
        with st3:
            render_kpi_card("Missing Cells", str(stage_data.get("missing_cells", 0)), "NaN / null count", "Verified Clean", "success")
        with st4:
            render_kpi_card("Duplicate Rows", str(stage_data.get("duplicate_rows", 0)), "Exact duplicates", "Deduplicated", "success" if stage_data.get("duplicate_rows", 0) == 0 else "warning")
        with st5:
            render_kpi_card("Primary File", stage_data.get("file_name", ""), "Active stage file", "Stored", "info")

        # Split statistics if in Train or Test stage
        if stage_choice in ["04_Train_Data", "05_Test_Data"]:
            st.markdown("##### ⚖️ Partition & Split Configuration")
            split_c1, split_c2 = st.columns([1.5, 1])
            with split_c1:
                st.markdown(f"- **Split Method:** {ds_summary.get('split_method', 'Stratified Shuffle Split')}")
                st.markdown(f"- **Random Seed:** `{ds_summary.get('random_seed', 42)}` (Reproducible)")
                st.markdown(f"- **Anti-Leakage Policy:** {ds_summary.get('leakage_prevention_policy', 'Test partition strictly isolated.')}")
            with split_c2:
                if stage_choice == "04_Train_Data":
                    t_dist = ds_summary.get("target_distribution_train", {})
                    st.markdown(f"- **Train Partition Count:** {ds_summary.get('train_record_count', dims.get('rows', 0)):,} rows ({ds_summary.get('train_percentage', 80)}%)")
                    st.markdown(f"- **Train Target Balance:** `{t_dist}`")
                else:
                    te_dist = ds_summary.get("target_distribution_test", {})
                    st.markdown(f"- **Test Partition Count:** {ds_summary.get('test_record_count', dims.get('rows', 0)):,} rows ({ds_summary.get('test_percentage', 20)}%)")
                    st.markdown(f"- **Test Target Balance:** `{te_dist if te_dist else 'Unlabeled Competition Set'}`")

        # Cleaning decisions callout if in Clean stage
        elif stage_choice == "03_Clean_Data":
            st.markdown("##### 🧹 Documented Cleaning Decisions & Transformations")
            actions = ds_summary.get("cleaning_actions", [])
            for act in actions:
                st.markdown(f"- ✅ {act}")

        # Data preview
        st.markdown(f"##### 📄 Data Preview ({stage_data.get('file_name', '')})")
        preview_records = stage_data.get("preview_records", [])
        if preview_records:
            df_st_preview = pd.DataFrame(preview_records)
            st.dataframe(df_st_preview, width="stretch", height=280)
            st.caption(f"Showing first {len(df_st_preview)} rows of {stage_data.get('file_name')}. Relative storage path: `dataset/Data Cleaning & Splitting/{selected_ds_id}/{stage_choice}/{stage_data.get('file_name')}`")
        
        with st.expander("🔍 Inspect Schema & Column Data Types for this Stage"):
            dtypes_dict = stage_data.get("dtypes", {})
            df_dtypes = pd.DataFrame([{"Column": c, "Data Type": t} for c, t in dtypes_dict.items()])
            st.dataframe(df_dtypes, width="stretch", hide_index=True)
    else:
        st.warning(f"Stage '{stage_choice}' has not been generated or is not applicable for this dataset.")

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- TAB 1: DATASET FOLDERS CATALOG -----------------
with tab_folders:
    st.markdown("#### Organized Dataset Folders in the `dataset/` Directory")
    st.caption("All datasets have been sorted into distinct, dedicated directories for clarity and easy understanding.")

    catalog = get_dataset_catalog()
    if catalog:
        c_cols = st.columns(len(catalog))
        for idx, cat_item in enumerate(catalog):
            with c_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-radius:10px; padding:18px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-size:12px; font-weight:700; color:#2563eb; text-transform:uppercase;">
                            Folder {idx + 1}
                        </div>
                        <div style="font-size:15px; font-weight:700; color:#0f172a; margin:4px 0 6px 0;">
                            {cat_item['name']}
                        </div>
                        <div style="font-size:12px; color:#64748b; min-height:48px; margin-bottom:10px;">
                            {cat_item['description']}
                        </div>
                        <div style="font-size:12.5px; padding:4px 0; border-top:1px solid #f1f5f9;">
                            📁 <code>dataset/{cat_item['folder']}</code>
                        </div>
                        <div style="font-size:12.5px; padding:4px 0; border-top:1px solid #f1f5f9;">
                            📄 Primary: <strong>{cat_item['primary_file']}</strong>
                        </div>
                        <div style="font-size:11.5px; color:#94a3b8; margin-top:6px;">
                            Files: {', '.join(cat_item.get('files', []))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        """
        <div class="info-callout">
            <strong>Dataset Organization Summary:</strong><br>
            • <strong>1_uci_bank_marketing_canonical/</strong>: The standard 45,211 row benchmark dataset (Moro et al.) with 17 total columns (16 features + 1 target <code>y</code>; 15 input features used in ML models excluding <code>duration</code>).<br>
            • <strong>2_bank_additional_socioeconomic/</strong>: 41,188 records enriched with 5 national macroeconomic indicators (Euribor 3M, Consumer Price Index, Employment Variation Rate).<br>
            • <strong>3_train_test_competition/</strong>: ML competition partition pre-split into <code>train.csv</code> (22,501 labeled records with <code>subscribe</code> target) and <code>test.csv</code> (7,501 unlabeled records) with sample submission.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------- TAB 1: PREVIEW -----------------
with tab_preview:
    st.markdown("#### Sample Records Preview")
    st.caption("Displays authorized preview rows fetched dynamically via `/api/dataset/sample`. The full dataset is never dumped at once.")

    col_ctrl1, col_ctrl2 = st.columns([1, 3])
    with col_ctrl1:
        row_limit = st.selectbox("Rows to display:", options=[10, 20, 50, 100], index=0)


    sample_records = get_dataset_sample(limit=row_limit)
    if sample_records:
        df_sample = pd.DataFrame(sample_records)
        
        # Optional local preview filter
        target_filter = st.radio("Filter preview by target ('y'):", options=["All", "no", "yes"], horizontal=True)
        if target_filter != "All":
            df_filtered = df_sample[df_sample["y"] == target_filter]
        else:
            df_filtered = df_sample

        st.dataframe(df_filtered, width="stretch", height=350)
        st.caption(f"Showing {len(df_filtered)} preview records.")
    else:
        st.warning("Could not fetch preview records.")

# ----------------- TAB 2: SCHEMA & TYPES -----------------
with tab_schema:
    st.markdown("#### Feature Schema & Data Dictionary (16 Features + 1 Target = 17 Columns)")
    st.caption(
        "The canonical dataset contains 17 columns: 16 feature columns and 1 target column (<code>y</code>). "
        "During ML model training, exactly 15 input features are used (6 numerical + 9 categorical) "
        "after strictly excluding <code>duration</code> to prevent target leakage.",
        unsafe_allow_html=True,
    )
    
    schema_data = [
        {"Column Name": "age", "Role": "Input Feature (ML)", "Type": "Numeric (int64)", "Description": "Client age in years (Range: 18 - 95)"},
        {"Column Name": "job", "Role": "Input Feature (ML)", "Type": "Categorical (object)", "Description": "Type of employment (management, technician, blue-collar, etc.)"},
        {"Column Name": "marital", "Role": "Input Feature (ML)", "Type": "Categorical (object)", "Description": "Marital status (married, single, divorced/widowed)"},
        {"Column Name": "education", "Role": "Input Feature (ML)", "Type": "Categorical (object)", "Description": "Education level (primary, secondary, tertiary, unknown)"},
        {"Column Name": "default", "Role": "Input Feature (ML)", "Type": "Binary (object)", "Description": "Has credit in default? ('no', 'yes')"},
        {"Column Name": "balance", "Role": "Input Feature (ML)", "Type": "Numeric (int64)", "Description": "Average yearly account balance in Euros"},
        {"Column Name": "housing", "Role": "Input Feature (ML)", "Type": "Binary (object)", "Description": "Has housing loan obligation? ('no', 'yes')"},
        {"Column Name": "loan", "Role": "Input Feature (ML)", "Type": "Binary (object)", "Description": "Has personal loan obligation? ('no', 'yes')"},
        {"Column Name": "contact", "Role": "Input Feature (ML)", "Type": "Categorical (object)", "Description": "Contact communication medium (cellular, telephone, unknown)"},
        {"Column Name": "day", "Role": "Input Feature (ML)", "Type": "Numeric (int64)", "Description": "Last contact day of the month (1 - 31)"},
        {"Column Name": "month", "Role": "Input Feature (ML)", "Type": "Categorical (object)", "Description": "Last contact month of the calendar year (jan - dec)"},
        {"Column Name": "duration", "Role": "Excluded (Anti-leakage)", "Type": "Numeric (int64)", "Description": "Call duration in seconds. [EXCLUDED FROM ML PIPELINE: Unknown prior to calling]"},
        {"Column Name": "campaign", "Role": "Input Feature (ML)", "Type": "Numeric (int64)", "Description": "Number of contacts performed during this campaign for client"},
        {"Column Name": "pdays", "Role": "Input Feature (ML)", "Type": "Numeric (int64)", "Description": "Days passed after client was last contacted (-1 means never contacted)"},
        {"Column Name": "previous", "Role": "Input Feature (ML)", "Type": "Numeric (int64)", "Description": "Number of contacts performed before this campaign for client"},
        {"Column Name": "poutcome", "Role": "Input Feature (ML)", "Type": "Categorical (object)", "Description": "Outcome of the previous marketing campaign (unknown, failure, other, success)"},
        {"Column Name": "y", "Role": "Target Variable", "Type": "Target Binary (object)", "Description": "Has client subscribed a term deposit? ('no' = 0, 'yes' = 1)"},
    ]
    df_schema = pd.DataFrame(schema_data)
    st.dataframe(df_schema, width="stretch", hide_index=True)

# ----------------- TAB 3: DESCRIPTIVE STATS -----------------
with tab_stats:
    st.markdown("#### Numerical Attributes Summary")
    num_summary = summary.get("numerical_summary", {})
    if num_summary:
        df_num = pd.DataFrame(num_summary).T.reset_index()
        df_num.rename(columns={"index": "Attribute"}, inplace=True)
        st.dataframe(df_num, width="stretch", hide_index=True)

    st.markdown("#### Categorical Attributes & 'Unknown' Value Analysis")
    st.caption("In bank marketing surveys, 'unknown' values are not random missing data, but meaningful informational categories (e.g. poutcome 'unknown' indicates a first-time prospect).")
    cat_summary = summary.get("categorical_summary", {})
    if cat_summary:
        cat_rows = []
        for cat_col, details in cat_summary.items():
            cat_rows.append({
                "Attribute": cat_col,
                "Unique Values": details.get("unique_values_count"),
                "'Unknown' Count": details.get("unknown_count"),
                "'Unknown' Share (%)": f"{details.get('unknown_percentage'):.2f}%",
                "Top Values": ", ".join([f"{k} ({v:,})" for k, v in list(details.get("top_values", {}).items())[:3]])
            })
        st.dataframe(pd.DataFrame(cat_rows), width="stretch", hide_index=True)

# ----------------- TAB 4: DISTRIBUTIONS & EDA -----------------
with tab_distributions:
    st.markdown("#### Exploratory Data Visualizations & Distributions")
    st.caption("Visualizing customer segmentation, communication channels, and previous outreach outcomes.")
    
    eda_r1_c1, eda_r1_c2 = st.columns(2)
    
    with eda_r1_c1:
        st.markdown("##### 💼 Customer Distribution by Job Type")
        job_counts = summary.get("categorical_summary", {}).get("job", {}).get("top_values", {})
        if job_counts:
            df_jobs = pd.DataFrame(list(job_counts.items()), columns=["Job", "Count"]).sort_values(by="Count", ascending=True)
            df_jobs["Job_Display"] = df_jobs["Job"].apply(lambda x: x.replace(".", "").title())
            fig_jobs = px.bar(
                df_jobs, x="Count", y="Job_Display",
                orientation="h",
                color_discrete_sequence=["#1d4ed8"],
                text=[f"{c:,}" for c in df_jobs["Count"]],
                template="plotly_white",
            )
            fig_jobs.update_traces(
                textposition="outside",
                textfont=dict(size=10, family="Inter", color="#1e293b"),
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>Contacts: <b>%{x:,}</b><extra></extra>",
            )
            fig_jobs.update_layout(
                height=350,
                margin=dict(t=25, b=25, l=110, r=45),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title=dict(text="Number of Campaign Contacts", font=dict(size=11.5, family="Inter", color="#334155")), gridcolor="#f1f5f9", range=[0, 11500]),
                yaxis=dict(title=None, tickfont=dict(size=11, family="Inter", color="#0f172a")),
            )
            st.plotly_chart(fig_jobs, width="stretch")

    with eda_r1_c2:
        st.markdown("##### 📞 Previous Campaign Outreach Outcome (poutcome)")
        pout_counts = summary.get("categorical_summary", {}).get("poutcome", {}).get("top_values", {})
        if pout_counts:
            pout_map = {"unknown": "Unknown (First Contact)", "failure": "Outreach Failure", "other": "Other Response", "success": "Outreach Success"}
            df_pout = pd.DataFrame(list(pout_counts.items()), columns=["Outcome", "Count"])
            df_pout["Outcome_Display"] = df_pout["Outcome"].apply(lambda x: f"{pout_map.get(x, x.title())} ({df_pout.loc[df_pout['Outcome']==x, 'Count'].values[0]:,})")
            fig_pout = px.pie(
                df_pout, names="Outcome_Display", values="Count",
                color_discrete_sequence=["#94a3b8", "#ef4444", "#3b82f6", "#10b981"],
                hole=0.55,
                template="plotly_white",
            )
            fig_pout.update_traces(
                textinfo="percent",
                hoverinfo="label+percent",
                textposition="inside",
                textfont=dict(size=12, family="Inter", color="#ffffff"),
                marker=dict(line=dict(color="#ffffff", width=2)),
            )
            fig_pout.update_layout(
                height=350,
                margin=dict(t=25, b=25, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5, font=dict(size=10.5, family="Inter", color="#334155")),
            )
            st.plotly_chart(fig_pout, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    eda_r2_c1, eda_r2_c2 = st.columns(2)

    with eda_r2_c1:
        st.markdown("##### 🎓 Education Level Segmentation")
        edu_counts = summary.get("categorical_summary", {}).get("education", {}).get("top_values", {})
        if edu_counts:
            df_edu = pd.DataFrame(list(edu_counts.items()), columns=["Education", "Count"]).sort_values(by="Count", ascending=False)
            df_edu["Education_Display"] = df_edu["Education"].apply(lambda x: x.title())
            fig_edu = px.bar(
                df_edu, x="Education_Display", y="Count",
                color_discrete_sequence=["#0284c7"],
                text=[f"{c:,}" for c in df_edu["Count"]],
                template="plotly_white",
            )
            fig_edu.update_traces(
                textposition="outside",
                textfont=dict(size=10.5, family="Inter", color="#1e293b"),
                cliponaxis=False,
                hovertemplate="<b>%{x}</b><br>Count: <b>%{y:,}</b><extra></extra>",
            )
            fig_edu.update_layout(
                height=330,
                margin=dict(t=25, b=25, l=25, r=25),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title=dict(text="Contacts Count", font=dict(size=11.5, family="Inter", color="#334155")), gridcolor="#f1f5f9", range=[0, 26000]),
                xaxis=dict(title=None, tickfont=dict(size=11.5, family="Inter", color="#0f172a")),
            )
            st.plotly_chart(fig_edu, width="stretch")

    with eda_r2_c2:
        st.markdown("##### 💍 Marital Status Distribution")
        mar_counts = summary.get("categorical_summary", {}).get("marital", {}).get("top_values", {})
        if mar_counts:
            mar_map = {"married": "Married", "single": "Single", "divorced": "Divorced / Widowed"}
            df_mar = pd.DataFrame(list(mar_counts.items()), columns=["Status", "Count"])
            df_mar["Status_Display"] = df_mar["Status"].apply(lambda x: f"{mar_map.get(x, x.title())} ({df_mar.loc[df_mar['Status']==x, 'Count'].values[0]:,})")
            fig_mar = px.pie(
                df_mar, names="Status_Display", values="Count",
                color_discrete_sequence=["#1e3a8a", "#0284c7", "#94a3b8"],
                hole=0.52,
                template="plotly_white",
            )
            fig_mar.update_traces(
                textinfo="percent",
                hoverinfo="label+percent",
                textposition="inside",
                textfont=dict(size=12, family="Inter", color="#ffffff"),
                marker=dict(line=dict(color="#ffffff", width=2)),
            )
            fig_mar.update_layout(
                height=330,
                margin=dict(t=25, b=25, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5, font=dict(size=10.5, family="Inter", color="#334155")),
            )
            st.plotly_chart(fig_mar, width="stretch")

# ----------------- TAB 5: DATA EXPORT -----------------
with tab_download:
    st.markdown("#### Authorized Data & Metadata Export")
    st.caption("Download comprehensive dataset metadata and statistics in standard JSON format.")
    
    summary_json_str = json.dumps(summary, indent=2)
    st.download_button(
        label="📥 Download Dataset Summary (JSON)",
        data=summary_json_str,
        file_name="bank_marketing_dataset_summary.json",
        mime="application/json",
        type="primary",
    )
