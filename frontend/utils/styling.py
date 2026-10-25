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

    /* Hide Streamlit Default Deploy Button, App Toolbar & Header Clutter */
    [data-testid="stToolbar"],
    .stDeployButton,
    [data-testid="stDecoration"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        opacity: 0 !important;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
        border-bottom: none !important;
        height: 0px !important;
        pointer-events: none !important;
    }

    [data-testid="stHeader"] button,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        pointer-events: auto !important;
        visibility: visible !important;
    }

    /* CRITICAL: Preserve Streamlit Icon Fonts & Ligatures (Eliminates 'keyboard_double' text leak) */
    [data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] svg,
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

    /* Explicitly preserve emoji font for emoji icons */
    [data-testid="stIconEmoji"] {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif !important;
    }

    /* Container constraints & breathing room - Prevents any clipping of page header banners */
    .block-container {
        padding-top: 1.75rem !important;
        padding-bottom: 2.75rem !important;
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
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 2px 0 12px rgba(15, 23, 42, 0.03) !important;
    }

    [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 1rem 1rem 1.5rem 1rem !important;
    }

    /* Re-order Sidebar so BankerEye Brand Header is firmly at the TOP */
    [data-testid="stSidebarHeader"] {
        order: 1 !important;
        padding: 0 !important;
        margin-bottom: 6px !important;
    }

    [data-testid="stSidebarUserContent"] {
        order: 2 !important;
        padding: 0 !important;
        margin-bottom: 4px !important;
    }

    [data-testid="stSidebarNav"] {
        order: 3 !important;
        padding-top: 6px !important;
    }

    [data-testid="stSidebarNav"]::before {
        content: "PLATFORM NAVIGATION" !important;
        display: block !important;
        font-size: 10.5px !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        padding: 6px 12px 6px 12px !important;
    }

    /* Sidebar Brand Card */
    .sidebar-brand-card {
        background: linear-gradient(145deg, #ffffff 0%, #f1f5f9 50%, #eff6ff 100%) !important;
        border: 1px solid #bfdbfe !important;
        border-radius: 12px !important;
        padding: 14px 14px 12px 14px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.07), 0 1px 2px rgba(15, 23, 42, 0.03) !important;
    }

    .sidebar-brand-badge {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }

    .sidebar-brand-logo {
        font-size: 24px !important;
        line-height: 1 !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 6px !important;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.05) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .sidebar-brand-names {
        display: flex !important;
        flex-direction: column !important;
    }

    .sidebar-brand-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
        line-height: 1.15 !important;
    }

    .sidebar-brand-accent {
        color: #2563eb !important;
    }

    .sidebar-brand-tagline {
        font-size: 10.5px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        margin-top: 2px !important;
    }

    .sidebar-brand-divider {
        height: 1px !important;
        background: #e2e8f0 !important;
        margin: 10px 0 8px 0 !important;
    }

    .sidebar-brand-status {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #047857 !important;
    }

    .status-indicator-dot {
        width: 7px !important;
        height: 7px !important;
        background-color: #10b981 !important;
        border-radius: 50% !important;
        display: inline-block !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25) !important;
        animation: pulse-dot 2s infinite ease-in-out !important;
    }

    @keyframes pulse-dot {
        0% { transform: scale(0.95); box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3); }
        50% { transform: scale(1.1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3); }
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
        padding: 9px 12px !important;
        margin: 2px 0 !important;
        transition: all 0.15s ease-in-out !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
    }

    [data-testid="stSidebarNav"] a:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
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

    /* Hub Navigation Cards (Unified inside bordered container) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 18px 20px 16px 20px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        height: 100% !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-3px) !important;
        border-color: #93c5fd !important;
        box-shadow: 0 12px 24px -4px rgba(37, 99, 235, 0.12), 0 4px 6px -2px rgba(15, 23, 42, 0.03) !important;
    }

    .nav-card-inner {
        flex-grow: 1 !important;
    }

    .nav-icon-badge {
        font-size: 26px !important;
        line-height: 1 !important;
        width: 44px !important;
        height: 44px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%) !important;
        border: 1px solid #dbeafe !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.05) !important;
    }

    .nav-card-title {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin-bottom: 6px !important;
        letter-spacing: -0.01em !important;
    }

    .nav-card-desc {
        font-size: 13px !important;
        color: #64748b !important;
        line-height: 1.55 !important;
        min-height: 42px !important;
        margin-bottom: 12px !important;
    }

    /* Embedded Page Link Button inside the Card */
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPageLink-NavLink"] a {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 9px 14px !important;
        color: #1e3a8a !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.18s ease-in-out !important;
        text-decoration: none !important;
        width: 100% !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPageLink-NavLink"] a:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border-color: #1d4ed8 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPageLink-NavLink"] a:hover * {
        color: #ffffff !important;
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


def render_sidebar_branding():
    """Renders executive BankerEye branding card at the top of the sidebar."""
    branding_html = """
    <div class="sidebar-brand-card">
        <div class="sidebar-brand-badge">
            <div class="sidebar-brand-logo">🏦</div>
            <div class="sidebar-brand-names">
                <div class="sidebar-brand-title">Banker<span class="sidebar-brand-accent">Eye</span></div>
                <div class="sidebar-brand-tagline">Term Deposit Intelligence</div>
            </div>
        </div>
        <div class="sidebar-brand-divider"></div>
        <div class="sidebar-brand-status">
            <span class="status-indicator-dot"></span>
            <span>Production ML &bull; Online</span>
        </div>
    </div>
    """
    st.sidebar.markdown(branding_html, unsafe_allow_html=True)

