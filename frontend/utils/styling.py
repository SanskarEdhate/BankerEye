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

    /* Streamlit App Header & Toolbar - Keep transparent & pass through clicks except to toolbar buttons */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        border-bottom: none !important;
        pointer-events: none !important;
        z-index: 999990 !important;
    }

    [data-testid="stToolbar"] {
        background-color: transparent !important;
        pointer-events: none !important;
        visibility: visible !important;
        display: flex !important;
    }

    /* Hide only unwanted right-hand toolbar clutter: Deploy Button, Status, MainMenu, Decoration, Footer */
    .stAppDeployButton,
    .stAppDeployButton *,
    .stDeployButton,
    .stDeployButton *,
    [data-testid="stAppDeployButton"],
    [data-testid="stAppDeployButton"] *,
    [data-testid="stDeployButton"],
    [data-testid="stDeployButton"] *,
    [data-testid="stDecoration"],
    #MainMenu,
    [data-testid="stToolbarActions"],
    [data-testid="stToolbarActionButton"],
    [data-testid="stStatusWidget"],
    [data-testid="stMainMenu"],
    header .stActionButton,
    footer {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
        overflow: hidden !important;
    }

    /* =========================================================================
       SIDEBAR CONTAINER & FLEX ORDER HIERARCHY
       ========================================================================= */
    section[data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebarContent"] {
        width: 280px !important;
        padding: 16px !important;
        background-color: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        min-height: 100vh !important;
        gap: 0 !important;
        box-sizing: border-box !important;
    }

    /* All direct children default to order: 10 */
    [data-testid="stSidebarContent"] > * {
        order: 10 !important;
    }

    /* 1. Header with collapse button at the top */
    [data-testid="stSidebarContent"] > [data-testid="stSidebarHeader"],
    [data-testid="stSidebarHeader"] {
        order: 1 !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        justify-content: flex-end !important;
        align-items: center !important;
        padding: 0 0 10px 0 !important;
        min-height: 36px !important;
        background: transparent !important;
    }

    /* Force collapse button wrapper to be visible */
    [data-testid="stSidebarHeader"] div,
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        opacity: 1 !important;
        display: flex !important;
    }

    /* Hide logo spacer so collapse button is at the top right */
    [data-testid="stLogoSpacer"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }

    /* Unbox User Content container so brand card & footer position seamlessly */
    [data-testid="stSidebarContent"] > [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarUserContent"] {
        display: contents !important;
    }

    /* 2. Brand Card: pinned directly below collapse header */
    .st-key-sidebar-brand {
        order: 2 !important;
        width: 100% !important;
        margin-bottom: 2px !important;
    }

    /* 3. Navigation page links cleanly below the branding card */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarContent"] > div:has([data-testid="stSidebarNav"]) {
        order: 3 !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 4. Footer pinned to bottom of sidebar */
    .st-key-sidebar-footer {
        order: 100 !important;
        margin-top: auto !important;
        width: 100% !important;
    }

    /* =========================================================================
       SIDEBAR TOGGLE BUTTONS (Expand & Collapse - Bulletproof Glyph Replacement)
       ========================================================================= */
    /* 1. EXPAND SIDEBAR BUTTON (Visible when sidebar is COLLAPSED) */
    [data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"] button,
    button[aria-label="Expand sidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        min-height: 36px !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.12) !important;
        cursor: pointer !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 9999999 !important;
        padding: 0 !important;
        margin: 0 !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stExpandSidebarButton"] button:hover,
    button[aria-label="Expand sidebar"]:hover {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2) !important;
    }

    /* 2. COLLAPSE SIDEBAR BUTTON (Visible when sidebar is OPEN) */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button,
    button[aria-label="Collapse sidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08) !important;
        cursor: pointer !important;
        position: relative !important;
        padding: 0 !important;
        margin: 0 !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    button[aria-label="Collapse sidebar"]:hover {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2) !important;
    }

    /* 3. ZERO-TOLERANCE TEXT LEAK SUPPRESSION
          Permanently eradicate any raw font ligatures:
          'keyboard_double_arrow_right' & 'keyboard_double_arrow_left' */
    [data-testid="stExpandSidebarButton"] span,
    [data-testid="stExpandSidebarButton"] * span,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] * span,
    button[aria-label="Expand sidebar"] span,
    button[aria-label="Expand sidebar"] * span,
    button[aria-label="Collapse sidebar"] span,
    button[aria-label="Collapse sidebar"] * span {
        display: none !important;
        visibility: hidden !important;
        font-size: 0px !important;
        line-height: 0 !important;
        width: 0 !important;
        height: 0 !important;
        color: transparent !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }

    /* 4. CRISP CHEVRON PSEUDO-ELEMENTS */
    /* Avoid duplicate chevrons on container div: */
    [data-testid="stExpandSidebarButton"]::after,
    [data-testid="stSidebarCollapseButton"]::after {
        content: none !important;
    }

    /* Expand button chevron (» points right to open sidebar) */
    [data-testid="stExpandSidebarButton"] button::after,
    button[aria-label="Expand sidebar"]::after {
        content: "»" !important;
        font-size: 24px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        pointer-events: none !important;
    }

    /* Collapse button chevron (« points left to close sidebar) */
    [data-testid="stSidebarCollapseButton"] button::after,
    button[aria-label="Collapse sidebar"]::after {
        content: "«" !important;
        font-size: 20px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        pointer-events: none !important;
    }

    [data-testid="stExpandSidebarButton"]:hover button::after,
    button[aria-label="Expand sidebar"]:hover::after,
    [data-testid="stSidebarCollapseButton"]:hover button::after,
    button[aria-label="Collapse sidebar"]:hover::after {
        color: #2563eb !important;
    }

    /* Preserve other Material symbols & Emojis */
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
        box-shadow: none !important;
    }

    /* Platform Navigation Section Header */
    [data-testid="stSidebarNav"]::before {
        content: "PLATFORM NAVIGATION" !important;
        display: block !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        margin-top: 16px !important;
        margin-bottom: 8px !important;
        padding: 0 12px !important;
    }

    [data-testid="stSidebarNav"] ul {
        padding: 0 !important;
        margin: 0 !important;
        list-style: none !important;
    }

    [data-testid="stSidebarNav"] li {
        margin-bottom: 2px !important;
    }

    /* Modern 40px Banking-Grade Nav Links */
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNavLink"] {
        height: 40px !important;
        min-height: 40px !important;
        max-height: 40px !important;
        border-radius: 10px !important;
        padding: 0 12px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #334155 !important;
        text-decoration: none !important;
        transition: all 150ms ease-in-out !important;
        background-color: transparent !important;
        border-left: 3px solid transparent !important;
        box-sizing: border-box !important;
    }

    [data-testid="stSidebarNav"] a span {
        transition: all 150ms ease-in-out !important;
    }

    /* Nav Item Icon (18px, Material symbols / Emojis) */
    [data-testid="stSidebarNav"] a span[data-testid="stIconMaterial"],
    [data-testid="stSidebarNav"] a svg,
    [data-testid="stSidebarNav"] a span:first-child {
        font-size: 18px !important;
        width: 18px !important;
        height: 18px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        flex-shrink: 0 !important;
    }

    /* Nav Item Label Text */
    [data-testid="stSidebarNav"] a span:last-child {
        font-size: 14px !important;
        font-weight: inherit !important;
        color: inherit !important;
        line-height: 1.2 !important;
    }

    /* Hover State */
    [data-testid="stSidebarNav"] a:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }

    [data-testid="stSidebarNav"] a:hover span {
        color: #0f172a !important;
    }

    /* Active State */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        border-left: 3px solid #2563eb !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #1d4ed8 !important;
        font-weight: 600 !important;
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

    /* Home Navigation Cards */
    .nav-card-inner {
        padding: 4px 0 10px 0;
    }

    .nav-icon-badge {
        font-size: 26px;
        line-height: 1;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
        border: 1px solid #e2e8f0;
    }

    .nav-card-title {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
        line-height: 1.3;
    }

    .nav-card-desc {
        font-size: 13px;
        color: #64748b;
        line-height: 1.5;
        min-height: 40px;
        margin-bottom: 8px;
    }

    /* Executive BankerEye Compact Sidebar Brand Card */
    .sidebar-brand-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        margin: 0 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        box-sizing: border-box !important;
    }

    .sidebar-brand-header {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }

    .sidebar-brand-logo-tile {
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        min-height: 38px !important;
        border-radius: 10px !important;
        background: #eff6ff !important;
        border: 1px solid #dbeafe !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
    }

    .sidebar-brand-text {
        display: flex !important;
        flex-direction: column !important;
        min-width: 0 !important;
    }

    .sidebar-brand-title {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        line-height: 1.2 !important;
        letter-spacing: -0.02em !important;
    }

    .sidebar-brand-accent {
        color: #2563eb !important;
        font-weight: 800 !important;
    }

    .sidebar-brand-tagline {
        font-size: 11px !important;
        font-weight: 500 !important;
        color: #64748b !important;
        line-height: 1.2 !important;
        margin-top: 2px !important;
        white-space: nowrap !important;
    }

    .sidebar-brand-divider {
        height: 1px !important;
        background: #f1f5f9 !important;
        margin: 10px 0 !important;
        border: none !important;
    }

    .sidebar-brand-status {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #16a34a !important;
        line-height: 1 !important;
    }

    .status-indicator-dot {
        width: 7px !important;
        height: 7px !important;
        border-radius: 50% !important;
        background-color: #16a34a !important;
        box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4) !important;
        display: inline-block !important;
        flex-shrink: 0 !important;
        animation: status-pulse 2s infinite cubic-bezier(0.4, 0, 0.6, 1) !important;
    }

    @keyframes status-pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.5);
        }
        70% {
            box-shadow: 0 0 0 5px rgba(22, 163, 74, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(22, 163, 74, 0);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .status-indicator-dot {
            animation: none !important;
            box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.2) !important;
        }
        [data-testid="stSidebarNav"] a {
            transition: none !important;
        }
    }

    /* Pinned Sidebar Footer */
    .sidebar-footer-card {
        width: 100% !important;
        margin-top: auto !important;
        padding-top: 14px !important;
        box-sizing: border-box !important;
    }

    .sidebar-footer-divider {
        height: 1px !important;
        background: #e2e8f0 !important;
        margin-bottom: 10px !important;
        border: none !important;
    }

    .sidebar-footer-meta {
        display: flex !important;
        flex-direction: column !important;
        gap: 3px !important;
        padding: 0 4px !important;
    }

    .sidebar-footer-version {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        line-height: 1.3 !important;
    }

    .sidebar-footer-copy {
        font-size: 11px !important;
        font-weight: 400 !important;
        color: #94a3b8 !important;
        line-height: 1.3 !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_sidebar_branding():
    """Renders compact executive BankerEye branding card at top of sidebar."""
    branding_html = """
    <div class="sidebar-brand-card">
        <div class="sidebar-brand-header">
            <div class="sidebar-brand-logo-tile">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 21h18"/>
                    <path d="M3 10h18"/>
                    <path d="M12 3L2 10h20L12 3z"/>
                    <path d="M6 10v7"/>
                    <path d="M10 10v7"/>
                    <path d="M14 10v7"/>
                    <path d="M18 10v7"/>
                    <circle cx="12" cy="13.5" r="1.5" fill="#2563eb"/>
                </svg>
            </div>
            <div class="sidebar-brand-text">
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
    st.markdown(branding_html, unsafe_allow_html=True)


def render_sidebar_footer():
    """Renders small muted metadata and copyright footer pinned to bottom of sidebar."""
    footer_html = """
    <div class="sidebar-footer-card">
        <div class="sidebar-footer-divider"></div>
        <div class="sidebar-footer-meta">
            <div class="sidebar-footer-version">v1.0.0 &bull; Enterprise ML</div>
            <div class="sidebar-footer-copy">&copy; BankerEye</div>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

