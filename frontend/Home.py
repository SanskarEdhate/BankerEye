import os
import sys
from pathlib import Path
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="BankerEye ML | Home",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.styling import apply_custom_css
from frontend.utils.api_client import check_api_health, get_dataset_summary, get_model_comparison
from frontend.components.cards import render_kpi_card, render_info_banner

apply_custom_css()

# Clean Sidebar: Only essential branding & live API status indicator
with st.sidebar:
    st.markdown("### 🏦 BankerEye ML")
    st.caption("Term Deposit Intelligence")
    st.markdown("---")

    health = check_api_health()
    if health.get("status") == "healthy":
        st.caption("🟢 **Flask API:** Online & Ready")
    else:
        st.caption("🔴 **Flask API:** Offline")

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

# 6 Clean Navigation Cards in a 3x2 Grid
nav_r1_c1, nav_r1_c2, nav_r1_c3 = st.columns(3)

with nav_r1_c1:
    st.markdown(
        """
        <div class="nav-card">
            <div>
                <div class="nav-icon">📊</div>
                <div class="nav-title">1. Dashboard</div>
                <div class="nav-desc">Executive KPI metrics, conversion donut charts, and model training status.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Dashboard.py", label="Open Executive Dashboard →", icon="📊", use_container_width=True)

with nav_r1_c2:
    st.markdown(
        """
        <div class="nav-card">
            <div>
                <div class="nav-icon">🔍</div>
                <div class="nav-title">2. Dataset Explorer</div>
                <div class="nav-desc">Organized dataset folders, feature schemas, missing values, and EDA distributions.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Dataset_Explorer.py", label="Explore Dataset & Catalog →", icon="🔍", use_container_width=True)

with nav_r1_c3:
    st.markdown(
        """
        <div class="nav-card">
            <div>
                <div class="nav-icon">⚖️</div>
                <div class="nav-title">3. Model Comparison</div>
                <div class="nav-desc">Side-by-side metric rankings, ROC curves, confusion matrices, and feature importance.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Model_Comparison.py", label="Compare 4 Classifiers →", icon="⚖️", use_container_width=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)

with nav_r2_c1:
    st.markdown(
        """
        <div class="nav-card">
            <div>
                <div class="nav-icon">🎯</div>
                <div class="nav-title">4. Subscription Predictor</div>
                <div class="nav-desc">Customer profiling form with 4-model consensus scoring and propensity gauges.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/4_Subscription_Predictor.py", label="Predict Customer Conversion →", icon="🎯", use_container_width=True)

with nav_r2_c2:
    st.markdown(
        """
        <div class="nav-card">
            <div>
                <div class="nav-icon">📁</div>
                <div class="nav-title">5. Batch Prediction</div>
                <div class="nav-desc">Upload bulk marketing CSV lead lists, perform batch scoring, and export CSV results.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/5_Batch_Prediction.py", label="Launch Batch Scoring →", icon="📁", use_container_width=True)

with nav_r2_c3:
    st.markdown(
        """
        <div class="nav-card">
            <div>
                <div class="nav-icon">📑</div>
                <div class="nav-title">6. Reports & Insights</div>
                <div class="nav-desc">Academic findings, verified literature review papers, and downloadable PDF reports.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/6_Reports_and_Insights.py", label="View Academic Reports →", icon="📑", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Subtle Academic Note at Bottom
render_info_banner(
    "Methodology Safeguard: Call duration is strictly excluded from all training pipelines to prevent post-call target leakage. "
    "Benchmarked on the canonical UCI Bank Marketing dataset (Moro et al.).",
    title="Anti-Leakage Architecture Notice"
)
