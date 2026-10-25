import os
import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.utils.styling import (
    apply_custom_css,
    render_sidebar_branding,
    render_sidebar_footer,
)

# Set root application configuration
st.set_page_config(
    page_title="BankerEye ML | Term Deposit Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. Single source of truth: Inject global styling once
apply_custom_css()

# 2. Render sidebar brand card and pinned footer once in keyed containers
with st.sidebar:
    with st.container(key="sidebar-brand"):
        render_sidebar_branding()

    with st.container(key="sidebar-footer"):
        render_sidebar_footer()

# Use Streamlit Navigation with resolved paths and Material icons
pages = [
    st.Page(FRONTEND_DIR / "views" / "Home.py", title="Home", icon=":material/home:", default=True),
    st.Page(FRONTEND_DIR / "views" / "1_Dashboard.py", title="Dashboard", icon=":material/dashboard:"),
    st.Page(FRONTEND_DIR / "views" / "2_Dataset_Explorer.py", title="Dataset Explorer", icon=":material/dataset:"),
    st.Page(FRONTEND_DIR / "views" / "3_Model_Comparison.py", title="Model Comparison", icon=":material/compare_arrows:"),
    st.Page(FRONTEND_DIR / "views" / "4_Subscription_Predictor.py", title="Subscription Predictor", icon=":material/psychology:"),
    st.Page(FRONTEND_DIR / "views" / "5_Batch_Prediction.py", title="Batch Prediction", icon=":material/upload_file:"),
    st.Page(FRONTEND_DIR / "views" / "6_Reports_and_Insights.py", title="Reports & Insights", icon=":material/description:"),
]

pg = st.navigation(pages)
pg.run()

