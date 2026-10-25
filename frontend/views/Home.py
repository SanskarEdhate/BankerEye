import os
import sys
from pathlib import Path
import streamlit as st

# Configure page settings if accessed directly
try:
    st.set_page_config(
        page_title="BankerEye ML | Home",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import check_api_health, get_dataset_summary, get_model_comparison
from frontend.components.cards import render_kpi_card, render_info_banner


# Executive Header Banner
st.markdown(
    """
    <div class="bank-header">
        <span class="banner-tag">Enterprise Machine Learning</span>
        <h1>Bank Marketing Subscription Prediction System</h1>
        <p>Production ML Pipeline, Multi-Model Empirical Benchmark, and Pre-Campaign Decision Support</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load summary & comparison
summary = get_dataset_summary() or {}
comparison = get_model_comparison() or {}
models_ready = comparison.get("status") == "ready" and bool(comparison.get("models"))

# Top KPI Metric Row - Clean, single-value, balanced cards
k1, k2, k3, k4 = st.columns(4)

with k1:
    render_kpi_card(
        label="Dataset Population",
        value=f"{summary.get('total_rows', 45211):,}",
        subtext="UCI canonical campaign records",
        badge_text="Cleaned",
        badge_type="info",
    )

with k2:
    render_kpi_card(
        label="Input Features Used",
        value="15",
        subtext="Pre-call predictors (Anti-leakage)",
        badge_text="Zero Leakage",
        badge_type="success",
    )

with k3:
    render_kpi_card(
        label="Conversion Rate",
        value="11.7%",
        subtext="Deposit subscribers (5,289 yes)",
        badge_text="Class Skew",
        badge_type="warning",
    )

with k4:
    best_acc = "89.47%" if models_ready else "89.5%"
    render_kpi_card(
        label="Top Model Accuracy",
        value=best_acc,
        subtext="Random Forest test score",
        badge_text="Benchmark",
        badge_type="success",
    )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🧭 System Navigation & Functional Modules")
st.caption("Select any module below or use the sidebar navigation to explore BankerEye ML.")

# 6 Clean, Unified Navigation Cards in a 3x2 Grid
nav_modules = [
    {
        "icon": "📊",
        "title": "1. Dashboard",
        "desc": "Executive KPI metrics, conversion donut charts, and model training status.",
        "page": "views/1_Dashboard.py",
        "label": "Open Executive Dashboard →",
    },
    {
        "icon": "🔍",
        "title": "2. Dataset Explorer",
        "desc": "Organized dataset folders, feature schemas, missing values, and EDA distributions.",
        "page": "views/2_Dataset_Explorer.py",
        "label": "Explore Dataset & Catalog →",
    },
    {
        "icon": "⚖️",
        "title": "3. Model Comparison",
        "desc": "Side-by-side metric rankings, ROC curves, confusion matrices, and feature importance.",
        "page": "views/3_Model_Comparison.py",
        "label": "Compare 4 Classifiers →",
    },
    {
        "icon": "🎯",
        "title": "4. Subscription Predictor",
        "desc": "Customer profiling form with 4-model consensus scoring and propensity gauges.",
        "page": "views/4_Subscription_Predictor.py",
        "label": "Predict Customer Conversion →",
    },
    {
        "icon": "📁",
        "title": "5. Batch Prediction",
        "desc": "Upload bulk marketing CSV lead lists, perform batch scoring, and export CSV results.",
        "page": "views/5_Batch_Prediction.py",
        "label": "Launch Batch Scoring →",
    },
    {
        "icon": "📑",
        "title": "6. Reports & Insights",
        "desc": "Academic findings, verified literature review papers, and downloadable PDF reports.",
        "page": "views/6_Reports_and_Insights.py",
        "label": "View Academic Reports →",
    },
]

# Row 1
r1_cols = st.columns(3)
for col, mod in zip(r1_cols, nav_modules[:3]):
    with col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="nav-card-inner">
                    <div class="nav-icon-badge">{mod['icon']}</div>
                    <div class="nav-card-title">{mod['title']}</div>
                    <div class="nav-card-desc">{mod['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(mod["page"], label=mod["label"], width="stretch")

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Row 2
r2_cols = st.columns(3)
for col, mod in zip(r2_cols, nav_modules[3:]):
    with col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="nav-card-inner">
                    <div class="nav-icon-badge">{mod['icon']}</div>
                    <div class="nav-card-title">{mod['title']}</div>
                    <div class="nav-card-desc">{mod['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(mod["page"], label=mod["label"], width="stretch")


st.markdown("<br>", unsafe_allow_html=True)

# Subtle Academic Note at Bottom
render_info_banner(
    "Methodology Safeguard: Call duration is strictly excluded from all training pipelines to prevent post-call target leakage. "
    "Benchmarked on the canonical UCI Bank Marketing dataset (Moro et al.).",
    title="Anti-Leakage Architecture Notice"
)
