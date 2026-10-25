import streamlit as st

def apply_custom_css():
    """Applies modern, clean, high-contrast light banking analytics stylesheet to Streamlit."""
    custom_css = """
    <style>
    /* Google Fonts Import - Inter, JetBrains Mono, and Material Symbols */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons&display=block');

    /* Global Root Variables - Enforce Crisp Light Mode */
    :root {
        --primary-color: #2563eb !important;
        --background-color: #f8fafc !important;
        --secondary-background-color: #ffffff !important;
        --text-color: #0f172a !important;
        --font: 'Inter', sans-serif !important;
    }

    /* Base Page & App Canvas */
    html, body {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        word-spacing: normal !important;
        letter-spacing: normal !important;
    }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    [data-testid="stHeader"] {
        background-color: #f8fafc !important;
        border-bottom: 1px solid rgba(226, 232, 240, 0.7) !important;
    }

    /* CRITICAL: Preserve Streamlit Icon Fonts & Ligatures (Eliminates 'keyboard_double' text leak) */
    [data-testid*="Icon"], 
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stIcon"],
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [class*="material-symbols"],
    [class*="material-icons"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons", sans-serif !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-feature-settings: 'liga' 1 !important;
    }

    /* Container constraints & padding */
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1240px !important;
    }

    /* Typography Defaults */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        letter-spacing: 0 !important;
        word-spacing: 0.05em !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    p, li, label {
        color: #334155 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px;
        line-height: 1.6;
        letter-spacing: normal !important;
        word-spacing: normal !important;
    }

    .stMarkdown p, .stMarkdown span, .stMarkdown li {
        font-family: 'Inter', sans-serif !important;
    }

    strong, b {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    /* Inline Code Formatting - Ensures margins prevent word concatenation */
    code {
        font-family: 'JetBrains Mono', SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        background-color: #f1f5f9 !important;
        color: #1e3a8a !important;
        padding: 2px 6px !important;
        border-radius: 5px !important;
        font-size: 0.88em !important;
        margin: 0 4px !important;
        border: 1px solid #e2e8f0 !important;
        display: inline-block !important;
        vertical-align: middle !important;
    }

    /* Streamlit Sidebar Enforcement (Clean White) */
    section[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 2px 0 8px rgba(15, 23, 42, 0.02) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    section[data-testid="stSidebar"] .stCaption, 
    section[data-testid="stSidebar"] small {
        color: #64748b !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #e2e8f0 !important;
        margin: 12px 0 !important;
    }

    /* Sidebar Navigation Links */
    [data-testid="stSidebarNav"] a {
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin: 2px 0 !important;
        transition: all 0.15s ease-in-out !important;
    }

    [data-testid="stSidebarNav"] a:hover {
        background-color: #f1f5f9 !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #eff6ff !important;
        border-left: 3px solid #2563eb !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #1d4ed8 !important;
        font-weight: 700 !important;
    }

    /* Executive Navy Gradient Banner */
    .bank-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%) !important;
        border-radius: 14px !important;
        padding: 24px 30px !important;
        color: #ffffff !important;
        margin-bottom: 22px !important;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25), 0 4px 10px -2px rgba(15, 23, 42, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .bank-header * {
        color: #ffffff !important;
    }

    .bank-header h1 {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        letter-spacing: normal !important;
        word-spacing: 0.05em !important;
        margin: 0 0 6px 0 !important;
    }

    .bank-header p {
        color: #e2e8f0 !important;
        font-size: 14px !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }

    .bank-header .banner-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        color: #ffffff !important;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    /* KPI Cards (Clean White with Soft Elevation) */
    .kpi-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 18px 20px !important;
        margin-bottom: 14px !important;
        min-height: 128px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02) !important;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease !important;
    }

    .kpi-card:hover {
        transform: translateY(-2px) !important;
        border-color: #cbd5e1 !important;
        box-shadow: 0 10px 20px -3px rgba(15, 23, 42, 0.07), 0 4px 6px -2px rgba(15, 23, 42, 0.03) !important;
    }

    .kpi-label {
        font-size: 11.5px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #64748b !important;
        margin-bottom: 6px !important;
    }

    .kpi-value {
        font-family: 'Inter', sans-serif !important;
        font-size: 21px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.25 !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        overflow: hidden !important;
    }

    .kpi-subtext {
        font-size: 12px !important;
        color: #64748b !important;
        margin-top: 6px !important;
        line-height: 1.4 !important;
    }

    /* Model Cards */
    .model-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    .model-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06) !important;
    }

    .model-card-best {
        border: 2px solid #2563eb !important;
        background: #f8fafc !important;
        position: relative;
    }

    /* Hub Navigation Cards */
    .nav-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 20px 22px !important;
        height: 100% !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }

    .nav-card:hover {
        transform: translateY(-3px) !important;
        border-color: #93c5fd !important;
        box-shadow: 0 12px 24px -4px rgba(37, 99, 235, 0.12), 0 4px 6px -2px rgba(15, 23, 42, 0.03) !important;
    }

    .nav-icon {
        font-size: 26px !important;
        margin-bottom: 10px !important;
    }

    .nav-title {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin-bottom: 6px !important;
    }

    .nav-desc {
        font-size: 13px !important;
        color: #64748b !important;
        line-height: 1.5 !important;
        margin-bottom: 14px !important;
    }

    /* Badges */
    .badge {
        display: inline-block !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
    }

    .badge-success {
        background-color: #ecfdf5 !important;
        color: #047857 !important;
        border: 1px solid #a7f3d0 !important;
    }

    .badge-warning {
        background-color: #fffbeb !important;
        color: #b45309 !important;
        border: 1px solid #fde68a !important;
    }

    .badge-info {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        border: 1px solid #bfdbfe !important;
    }

    .badge-danger {
        background-color: #fef2f2 !important;
        color: #b91c1c !important;
        border: 1px solid #fecaca !important;
    }

    /* Callout Notice */
    .info-callout {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 4px solid #2563eb !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin: 14px 0 !important;
        font-size: 13.5px !important;
        color: #334155 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
    }

    .info-callout strong {
        color: #0f172a !important;
    }

    /* Input Widgets, Selects, Number inputs */
    input, select, textarea, div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: #cbd5e1 !important;
    }

    div[data-baseweb="select"] * {
        color: #0f172a !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.1) !important;
        border-radius: 8px !important;
    }

    li[role="option"] {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }

    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #0f172a !important;
    }

    .stButton > button:hover {
        border-color: #2563eb !important;
        color: #2563eb !important;
        background: #eff6ff !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
        transform: translateY(-1px) !important;
        color: #ffffff !important;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid #e2e8f0 !important;
        gap: 6px !important;
    }

    button[data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        padding: 8px 16px !important;
        border-radius: 8px 8px 0 0 !important;
        border-bottom: 2px solid transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb !important;
        background-color: rgba(37, 99, 235, 0.06) !important;
    }

    /* Dataframe / Tables */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }

    /* Plotly Chart Card Container */
    .chart-container {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
    }

    /* Alerts */
    .stAlert {
        border-radius: 10px !important;
        font-size: 13.5px !important;
    }

    /* Links */
    a {
        color: #2563eb !important;
        text-decoration: none !important;
        font-weight: 600 !important;
    }

    a:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
