import streamlit as st
from typing import Optional

def render_kpi_card(
    label: str,
    value: str,
    subtext: Optional[str] = None,
    badge_text: Optional[str] = None,
    badge_type: str = "info",
):
    """Renders a clean, high-contrast KPI metric card."""
    badge_html = ""
    if badge_text:
        badge_html = f"<span class='badge badge-{badge_type}' style='float:right;'>{badge_text}</span>"

    subtext_html = ""
    if subtext:
        subtext_html = f"<div class='kpi-subtext'>{subtext}</div>"

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label} {badge_html}</div>
        <div class="kpi-value">{value}</div>
        {subtext_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_info_banner(text: str, title: Optional[str] = None):
    """Renders a subtle informational note banner."""
    title_html = f"<strong>{title}</strong><br>" if title else ""
    st.markdown(
        f"""
        <div class="info-callout">
            {title_html}{text}
        </div>
        """,
        unsafe_allow_html=True,
    )
