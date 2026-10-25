import os
import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Use Streamlit Navigation to enforce clean page titles and icons across all routes
pages = [
    st.Page("Home.py", title="Home", icon="🏦", default=True),
    st.Page("pages/1_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/2_Dataset_Explorer.py", title="Dataset Explorer", icon="🔍"),
    st.Page("pages/3_Model_Comparison.py", title="Model Comparison", icon="⚖️"),
    st.Page("pages/4_Subscription_Predictor.py", title="Subscription Predictor", icon="🎯"),
    st.Page("pages/5_Batch_Prediction.py", title="Batch Prediction", icon="📁"),
    st.Page("pages/6_Reports_and_Insights.py", title="Reports and Insights", icon="📑"),
]

pg = st.navigation(pages)
pg.run()
