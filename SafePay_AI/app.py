"""SafePay AI — Trust Before Transfer.

Streamlit prototype dashboard for detecting possible transaction coercion and
scam intent by analysing synthetic customer behaviour and transaction context.
"""

import datetime
import html
import math
import streamlit as st

from customer_data import (
    calculate_behaviour_profile,
    get_customer_history,
    get_customer_names,
)
from risk_engine import analyse_transaction, get_engine_status


st.set_page_config(
    page_title="SafePay AI — Trust Before Transfer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css() -> None:
    """Apply dark navy cybersecurity theme, glowing network background, and glass cards."""
    st.markdown(
        """
<style>
:root {
    --navy-950: #040916;
    --navy-900: #071226;
    --blue-800: #0c2244;
    --teal-500: #14b8a6;
    --teal-400: #2dd4bf;
    --cyan-400: #38bdf8;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --glass-bg: rgba(12, 27, 54, 0.58);
    --glass-border: rgba(56, 189, 248, 0.18);
    --glass-hover-border: rgba(45, 212, 191, 0.45);
}

/* Main App Background: Dark Navy, Deep Blue & Teal Gradient + CSS Network Pattern */
.stApp {
    background-color: var(--navy-950);
    background-image:
        radial-gradient(circle at 15% 18%, rgba(20, 184, 166, 0.16) 0%, transparent 38%),
        radial-gradient(circle at 85% 20%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 50% 88%, rgba(14, 116, 144, 0.14) 0%, transparent 45%),
        radial-gradient(rgba(45, 212, 191, 0.14) 1px, transparent 1px),
        linear-gradient(135deg, #040916 0%, #07142b 48%, #072235 100%);
    background-size:
        100% 100%,
        100% 100%,
        100% 100%,
        34px 34px,
        100% 100%;
    background-attachment: fixed;
    color: var(--text-primary);
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Subtle diagonal cyber grid overlay */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(to right, rgba(56, 189, 248, 0.035) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(56, 189, 248, 0.035) 1px, transparent 1px);
    background-size: 68px 68px;
    mask-image: radial-gradient(circle at center, black 35%, transparent 90%);
    z-index: 0;
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2.5rem;
    max-width: 1240px;
    position: relative;
    z-index: 1;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(6, 15, 33, 0.96) 0%, rgba(7, 25, 46, 0.94) 100%);
    border-right: 1px solid rgba(56, 189, 248, 0.16);
}

[data-testid="stSidebar"] * {
    color: var(--text-primary);
}

/* Hide default Streamlit header chrome clutter while preserving sidebar toggle */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Hero Banner */
.hero-shell {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.35rem 1.75rem;
    margin-bottom: 1.15rem;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(13, 33, 66, 0.78) 0%, rgba(10, 42, 61, 0.68) 100%);
    border: 1px solid rgba(45, 212, 191, 0.25);
    box-shadow:
        0 18px 40px rgba(2, 8, 23, 0.55),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 1.15rem;
}

.shield-logo {
    width: 60px;
    height: 60px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, rgba(20, 184, 166, 0.22), rgba(56, 189, 248, 0.16));
    border: 1px solid rgba(45, 212, 191, 0.45);
    box-shadow: 0 0 24px rgba(20, 184, 166, 0.28);
    flex-shrink: 0;
}

.hero-title {
    margin: 0;
    font-size: 1.85rem;
    font-weight: 750;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #f8fafc 0%, #bae6fd 52%, #5eead4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
}

.hero-subtitle {
    margin: 0.3rem 0 0 0;
    font-size: 0.98rem;
    color: #cbd5e1;
    font-weight: 450;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.48rem 0.95rem;
    border-radius: 999px;
    background: rgba(15, 118, 110, 0.22);
    border: 1px solid rgba(45, 212, 191, 0.45);
    color: #99f6e4;
    font-size: 0.84rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
    box-shadow: 0 0 18px rgba(20, 184, 166, 0.18);
}

.status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #2dd4bf;
    box-shadow: 0 0 10px #2dd4bf;
    animation: pulseGlow 2.2s infinite ease-in-out;
}

@keyframes pulseGlow {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.55; transform: scale(1.22); }
}

/* Navigation Pills styling over 4-option top st.radio */
div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label:nth-child(4)) > div[role="radiogroup"] {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.65rem;
    padding: 0.45rem;
    border-radius: 16px;
    background: rgba(9, 21, 45, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.16);
    backdrop-filter: blur(12px);
    margin-bottom: 1.25rem;
}

div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label:nth-child(4)) > div[role="radiogroup"] label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 11px;
    padding: 0.5rem 1.05rem;
    margin: 0 !important;
    cursor: pointer;
    transition: all 0.22s ease;
}

div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label:nth-child(4)) > div[role="radiogroup"] label:hover {
    background: rgba(56, 189, 248, 0.1);
    border-color: rgba(45, 212, 191, 0.35);
    transform: translateY(-1px);
}

div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label:nth-child(4)) > div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.26), rgba(56, 189, 248, 0.22));
    border-color: rgba(45, 212, 191, 0.55);
    box-shadow: 0 6px 18px rgba(20, 184, 166, 0.2);
}

div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label:nth-child(4)) > div[role="radiogroup"] label > div:first-child {
    display: none;
}

div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label:nth-child(4)) > div[role="radiogroup"] label p {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

/* Yes/No Radio Controls inside Safety Verification */
div[data-testid="stRadio"]:not(:has(> div[role="radiogroup"] > label:nth-child(4))) > div[role="radiogroup"] {
    gap: 1.15rem;
    padding: 0.35rem 0.25rem;
}

div[data-testid="stRadio"]:not(:has(> div[role="radiogroup"] > label:nth-child(4))) > div[role="radiogroup"] label {
    background: rgba(7, 18, 38, 0.72);
    border: 1px solid rgba(56, 189, 248, 0.24);
    border-radius: 10px;
    padding: 0.38rem 0.95rem;
    transition: all 0.2s ease;
}

div[data-testid="stRadio"]:not(:has(> div[role="radiogroup"] > label:nth-child(4))) > div[role="radiogroup"] label:has(input:checked) {
    background: rgba(20, 184, 166, 0.2);
    border-color: rgba(45, 212, 191, 0.55);
}

div[data-testid="stRadio"]:not(:has(> div[role="radiogroup"] > label:nth-child(4))) > div[role="radiogroup"] label p {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}

/* Welcome Hero Card */
.welcome-hero {
    background: linear-gradient(135deg, rgba(13, 35, 70, 0.76) 0%, rgba(11, 51, 66, 0.62) 100%);
    border: 1px solid rgba(45, 212, 191, 0.32);
    border-radius: 20px;
    padding: 1.45rem 1.7rem;
    margin-bottom: 1.1rem;
    box-shadow:
        0 14px 36px rgba(2, 8, 23, 0.48),
        0 0 28px rgba(20, 184, 166, 0.12);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    transition: border-color 0.24s ease, box-shadow 0.24s ease;
}

.welcome-hero:hover {
    border-color: rgba(45, 212, 191, 0.55);
    box-shadow:
        0 18px 42px rgba(2, 8, 23, 0.55),
        0 0 34px rgba(20, 184, 166, 0.2);
}

.welcome-title {
    margin: 0 0 0.45rem 0;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.015em;
    background: linear-gradient(90deg, #f8fafc 0%, #7dd3fc 55%, #5eead4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-desc {
    margin: 0;
    font-size: 0.98rem;
    line-height: 1.55;
    color: #dbeafe;
    max-width: 820px;
}

.verify-question-label {
    font-size: 0.95rem;
    font-weight: 650;
    color: #f1f5f9;
    margin-top: 0.55rem;
    margin-bottom: 0.15rem;
}

/* Glassmorphism Cards */
.glass-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    padding: 1.25rem 1.35rem;
    box-shadow: 0 12px 30px rgba(2, 8, 23, 0.42);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    transition: transform 0.24s ease, border-color 0.24s ease, box-shadow 0.24s ease;
    height: 100%;
}

.glass-card:hover {
    transform: translateY(-3px);
    border-color: var(--glass-hover-border);
    box-shadow:
        0 16px 36px rgba(2, 8, 23, 0.55),
        0 0 22px rgba(20, 184, 166, 0.14);
}

.card-tag {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5eead4;
    background: rgba(20, 184, 166, 0.14);
    border: 1px solid rgba(45, 212, 191, 0.28);
    padding: 0.24rem 0.6rem;
    border-radius: 999px;
    margin-bottom: 0.7rem;
}

.card-title {
    margin: 0 0 0.45rem 0;
    font-size: 1.06rem;
    font-weight: 680;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-body {
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.55;
    color: #cbd5e1;
}

.metric-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.metric-value {
    font-size: 1.45rem;
    font-weight: 750;
    color: #f8fafc;
    line-height: 1.2;
}

.metric-sub {
    margin-top: 0.35rem;
    font-size: 0.82rem;
    color: #5eead4;
}

.section-heading {
    font-size: 1.18rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0.35rem 0 0.9rem 0;
    display: flex;
    align-items: center;
    gap: 0.55rem;
}

/* Payee Pills */
.pill-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.55rem;
}

.payee-pill {
    font-size: 0.8rem;
    color: #e0f2fe;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.28);
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
}

/* Styled Transaction Table */
.table-shell {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    padding: 0.5rem 0.9rem;
    box-shadow: 0 12px 30px rgba(2, 8, 23, 0.42);
    backdrop-filter: blur(14px);
    overflow-x: auto;
}

.safepay-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.safepay-table th {
    text-align: left;
    padding: 0.85rem 0.75rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #94a3b8;
    border-bottom: 1px solid rgba(56, 189, 248, 0.18);
}

.safepay-table td {
    padding: 0.82rem 0.75rem;
    color: #e2e8f0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.safepay-table tbody tr {
    transition: background-color 0.18s ease;
}

.safepay-table tbody tr:hover {
    background: rgba(45, 212, 191, 0.08);
}

.safepay-table tbody tr:last-child td {
    border-bottom: none;
}

.channel-badge {
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 8px;
    font-size: 0.76rem;
    font-weight: 600;
    color: #99f6e4;
    background: rgba(20, 184, 166, 0.16);
    border: 1px solid rgba(45, 212, 191, 0.3);
}

.amount-cell {
    font-weight: 700;
    color: #f8fafc;
    font-variant-numeric: tabular-nums;
}

/* Placeholder visual flow */
.placeholder-banner {
    border: 1px dashed rgba(45, 212, 191, 0.38);
    background: rgba(8, 24, 48, 0.5);
    border-radius: 16px;
    padding: 1rem 1.25rem;
    color: #cbd5e1;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

/* Input controls styling inside dark glass theme */
[data-testid="stForm"] {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    padding: 1.25rem 1.35rem 1.35rem 1.35rem;
    box-shadow: 0 12px 30px rgba(2, 8, 23, 0.42);
    backdrop-filter: blur(14px);
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTimeInput"] input,
div[data-testid="stTextArea"] textarea {
    background-color: rgba(7, 18, 38, 0.82) !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 12px !important;
}

div[data-testid="stSelectbox"] > div > div {
    background-color: rgba(7, 18, 38, 0.82) !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 12px !important;
}

/* Primary Analyse Transaction button */
div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.96rem !important;
    letter-spacing: 0.02em;
    border: 1px solid rgba(45, 212, 191, 0.55) !important;
    border-radius: 12px !important;
    padding: 0.65rem 1.4rem !important;
    box-shadow: 0 8px 22px rgba(20, 184, 166, 0.28) !important;
    transition: all 0.22s ease !important;
    width: 100%;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(45, 212, 191, 0.4) !important;
    border-color: #5eead4 !important;
}

/* Risk Result Visualisation */
.risk-hero-card {
    background: var(--glass-bg);
    border-radius: 20px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 14px 34px rgba(2, 8, 23, 0.48);
    backdrop-filter: blur(16px);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1.6rem;
    margin-bottom: 1rem;
}

.gauge-box {
    flex: 0 0 184px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.risk-summary-box {
    flex: 1 1 280px;
}

.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.34rem 0.85rem;
    border-radius: 999px;
    font-size: 0.84rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.65rem;
}

.risk-big-score {
    font-size: 2.15rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 0.45rem 0;
    color: #f8fafc;
}

.risk-disclaimer {
    margin-top: 0.75rem;
    padding: 0.65rem 0.9rem;
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.22);
    color: #cbd5e1;
    font-size: 0.84rem;
    line-height: 1.45;
}

.factor-list {
    list-style: none;
    padding: 0;
    margin: 0.35rem 0 0 0;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}

.factor-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.65rem 0.85rem;
    border-radius: 12px;
    background: rgba(7, 18, 38, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.14);
    color: #e2e8f0;
    font-size: 0.89rem;
    line-height: 1.45;
}

.compare-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    margin-top: 0.65rem;
}

.compare-chip {
    font-size: 0.8rem;
    color: #e2e8f0;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 10px;
    padding: 0.35rem 0.7rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the SafePay AI shield logo, title, subtitle, and status pill."""
    shield_svg = (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<path d="M12 2.5L4.5 5.8V11.5C4.5 16.4 7.7 20.8 12 22C16.3 20.8 19.5 16.4 19.5 11.5V5.8L12 2.5Z" '
        'stroke="#2dd4bf" stroke-width="1.9" fill="rgba(45, 212, 191, 0.14)"/>'
        '<path d="M9.2 12.1L11.1 14L15 9.9" stroke="#f8fafc" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )

    st.markdown(
        f"""
<div class="hero-shell">
    <div class="hero-brand">
        <div class="shield-logo">{shield_svg}</div>
        <div>
            <h1 class="hero-title">SafePay AI &mdash; Trust Before Transfer</h1>
            <p class="hero-subtitle">Transaction Coercion and Scam-Intent Verification</p>
        </div>
    </div>
    <div class="status-pill">
        <span class="status-dot"></span>
        <span>Prototype Active</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Render sidebar controls for synthetic customer selection and prototype context."""
    with st.sidebar:
        st.markdown("### 🛡️ SafePay Control Panel")
        st.caption("Select a fictional customer profile to inspect baseline behaviour.")

        customer_names = get_customer_names()
        selected_customer = st.selectbox(
            "Synthetic Customer Profile",
            options=customer_names,
            index=0,
        )

        engine_info = get_engine_status()
        st.markdown("---")
        st.markdown("#### System Scope")
        st.info(
            f"**Engine:** {engine_info['engine_name']}\n\n"
            f"**Mode:** {engine_info['mode']}\n\n"
            "All customer records are **100% synthetic**. "
            "No real bank connection, payment execution, or phone calls."
        )

    return selected_customer


def render_glass_card(tag: str, title: str, body: str) -> str:
    """Return HTML markup for a reusable glassmorphism placeholder card."""
    return (
        '<div class="glass-card">'
        f'<div class="card-tag">{html.escape(tag)}</div>'
        f'<div class="card-title">{title}</div>'
        f'<p class="card-body">{html.escape(body)}</p>'
        "</div>"
    )


def render_overview_section(selected_customer: str) -> None:
    """Render the polished Welcome banner and Overview dashboard cards."""
    st.markdown(
        """
<div class="welcome-hero">
    <div class="card-tag">Trust Before Transfer</div>
    <h2 class="welcome-title">Your Safety. Your Payment. Your Choice.</h2>
    <p class="welcome-desc">
        SafePay AI analyses transaction behaviour and context to identify possible coercion
        and recommend safer payment decisions.
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">🌐 Platform Overview</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown(
            render_glass_card(
                "Core Mission",
                "🛡️ Pre-Transfer Shield",
                "Evaluates whether an outgoing transfer aligns with a customer's normal "
                "financial habits before funds leave the account.",
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            render_glass_card(
                "Threat Focus",
                "🎭 Coercion & Scam Signals",
                "Designed to spot urgency pressure, unfamiliar payees, unusual transfer "
                "hours, remote-access hints, and sudden amount spikes.",
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            render_glass_card(
                "Prototype Guardrail",
                "🧪 Synthetic Sandbox",
                f"Currently inspecting fictional baseline profile for {selected_customer}. "
                "No live banking APIs, real payments, or real phone calls are connected.",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.3, 1], gap="medium")
    with c_left:
        st.markdown(
            render_glass_card(
                "Architecture Flow",
                "⚡ How SafePay AI Works",
                "1. Load synthetic customer baseline  →  "
                "2. Inspect incoming transaction context  →  "
                "3. Score multi-signal coercion indicators  →  "
                "4. Trigger calm safety verification when high-risk cues appear.",
            ),
            unsafe_allow_html=True,
        )
    with c_right:
        st.markdown(
            render_glass_card(
                "Prototype Status",
                "🧩 End-to-End Flow Ready",
                "Customer History, Transaction Analysis, explainable 0–100 risk scoring, "
                "and simulated Safety Verification are all connected and interactive.",
            ),
            unsafe_allow_html=True,
        )


def _get_risk_palette(risk_category: str) -> dict:
    """Return Teal / Amber / Red theme tokens for Low, Medium, or High risk."""
    category = risk_category.strip().lower()
    if category == "high":
        return {
            "accent": "#ef4444",
            "accent_soft": "#fca5a5",
            "bg": "rgba(239, 68, 68, 0.15)",
            "border": "rgba(239, 68, 68, 0.48)",
            "glow": "rgba(239, 68, 68, 0.28)",
            "icon": "🚨",
        }
    if category == "medium":
        return {
            "accent": "#f59e0b",
            "accent_soft": "#fde68a",
            "bg": "rgba(245, 158, 11, 0.15)",
            "border": "rgba(245, 158, 11, 0.48)",
            "glow": "rgba(245, 158, 11, 0.25)",
            "icon": "⚠️",
        }
    return {
        "accent": "#14b8a6",
        "accent_soft": "#99f6e4",
        "bg": "rgba(20, 184, 166, 0.16)",
        "border": "rgba(45, 212, 191, 0.5)",
        "glow": "rgba(20, 184, 166, 0.26)",
        "icon": "🛡️",
    }


def render_risk_result_visualisation(result: dict) -> None:
    """Render responsive circular gauge, risk factors, and safety guidance."""
    score = int(result["risk_score"])
    category = str(result["risk_category"])
    reasons = result.get("reasons", [])
    recommendation = str(result.get("recommended_action", ""))
    comparison = result.get("baseline_comparison", {})
    palette = _get_risk_palette(category)

    # SVG circular gauge geometry (radius = 70 -> circumference = 439.82)
    radius = 70
    circumference = 2 * math.pi * radius
    offset = circumference * (1.0 - max(0, min(100, score)) / 100.0)

    gauge_svg = (
        f'<svg width="176" height="176" viewBox="0 0 180 180" '
        f'style="filter: drop-shadow(0 0 14px {palette["glow"]});">'
        '<circle cx="90" cy="90" r="70" fill="none" '
        'stroke="rgba(148, 163, 184, 0.18)" stroke-width="14" />'
        f'<circle cx="90" cy="90" r="70" fill="none" stroke="{palette["accent"]}" '
        'stroke-width="14" stroke-linecap="round" '
        f'stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" '
        'transform="rotate(-90 90 90)" />'
        f'<text x="90" y="88" text-anchor="middle" fill="#f8fafc" '
        'font-size="38" font-weight="800" font-family="Inter, Segoe UI, sans-serif">'
        f'{score}</text>'
        '<text x="90" y="112" text-anchor="middle" fill="#94a3b8" '
        'font-size="13" font-weight="600" font-family="Inter, Segoe UI, sans-serif">'
        'OUT OF 100</text>'
        "</svg>"
    )

    payee_status = (
        "Familiar Payee" if comparison.get("is_familiar_payee") else "New / Unfamiliar Payee"
    )
    avg_disp = float(comparison.get("historical_average", 0.0) or 0.0)
    usual_disp = str(comparison.get("usual_timing", "N/A"))
    tx_time_disp = str(comparison.get("payment_time", "N/A"))

    st.markdown(
        f"""
<div class="risk-hero-card" style="border: 1px solid {palette["border"]};">
    <div class="gauge-box">{gauge_svg}</div>
    <div class="risk-summary-box">
        <div class="risk-badge" style="color: {palette["accent_soft"]}; background: {palette["bg"]}; border: 1px solid {palette["border"]};">
            <span>{palette["icon"]}</span>
            <span>{html.escape(category)} Risk</span>
        </div>
        <div class="risk-big-score">Score: {score} / 100</div>
        <div class="compare-strip">
            <span class="compare-chip">Customer: <strong>{html.escape(str(comparison.get("customer_name", "")))}</strong></span>
            <span class="compare-chip">Historical Avg: <strong>₹{avg_disp:,.2f}</strong></span>
            <span class="compare-chip">Recipient: <strong>{html.escape(payee_status)}</strong></span>
            <span class="compare-chip">Time: <strong>{html.escape(tx_time_disp)}</strong> (Usual: {html.escape(usual_disp)})</span>
        </div>
        <div class="risk-disclaimer">
            Risk score represents the presence of possible coercion indicators. It is not proof of fraud.
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    col_factors, col_action = st.columns([1.25, 1], gap="medium")
    with col_factors:
        factor_items_html = "".join(
            f'<li class="factor-item"><span style="color:{palette["accent"]}; font-weight:700;">&bull;</span>'
            f'<span>{html.escape(str(reason))}</span></li>'
            for reason in reasons
        )
        st.markdown(
            f"""
<div class="glass-card">
    <div class="card-tag">Explainable Signals</div>
    <div class="card-title">🔎 Risk Factors &amp; Baseline Comparison</div>
    <ul class="factor-list">{factor_items_html}</ul>
</div>
            """,
            unsafe_allow_html=True,
        )

    with col_action:
        st.markdown(
            f"""
<div class="glass-card" style="border-color: {palette["border"]};">
    <div class="card-tag" style="color: {palette["accent_soft"]}; background: {palette["bg"]}; border-color: {palette["border"]};">
        Trust Before Transfer
    </div>
    <div class="card-title">{palette["icon"]} Recommended Safety Action</div>
    <p class="card-body" style="font-size: 0.96rem; color: #f1f5f9;">{html.escape(recommendation)}</p>
    <p class="card-body" style="margin-top: 0.85rem; font-size: 0.82rem; color: #94a3b8;">
        Prototype simulation only &mdash; no real payment is processed or blocked.
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )


def _activate_safety_verification() -> None:
    """Switch to the Safety Verification screen after high-risk detection."""
    st.session_state["verification_active"] = True
    st.session_state["nav_section"] = "Safety Verification"


def render_transaction_analysis_section(selected_customer: str) -> None:
    """Render interactive Transaction Analysis inputs and explainable risk results."""
    st.markdown(
        '<div class="section-heading">🔍 Transaction Analysis &mdash; Coercion &amp; Scam-Intent Check</div>',
        unsafe_allow_html=True,
    )

    customer_names = get_customer_names()
    default_idx = (
        customer_names.index(selected_customer) if selected_customer in customer_names else 0
    )

    with st.form("transaction_analysis_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            analysis_customer = st.selectbox(
                "Customer",
                options=customer_names,
                index=default_idx,
                key="ta_customer",
            )
        with c2:
            payment_amount = st.number_input(
                "Payment Amount (₹)",
                min_value=1.0,
                max_value=10000000.0,
                value=2500.0,
                step=500.0,
                key="ta_amount",
            )
        with c3:
            payment_time = st.time_input(
                "Payment Time",
                value=datetime.time(14, 30),
                key="ta_time",
            )

        c4, c5 = st.columns([1.1, 1], gap="medium")
        with c4:
            payee = st.text_input(
                "Payee",
                value="FreshMart Groceries",
                placeholder="Enter recipient name (e.g., FreshMart Groceries or Tech Support Desk)",
                key="ta_payee",
            )
        with c5:
            session_behaviour = st.selectbox(
                "Session Behaviour",
                options=[
                    "Normal & Calm Session",
                    "Hurried / Rushed Navigation",
                    "Hesitant / Repeated Input Edits",
                    "Possible Remote-Access Tool Hint (Screen Share / AnyDesk)",
                    "Hurried Session + Remote-Access Hint",
                ],
                index=0,
                key="ta_session",
            )

        payment_reason = st.text_area(
            "Payment Reason / Context",
            value="Monthly groceries and household supplies",
            placeholder=(
                "Describe why the payment is being made "
                "(e.g., 'Caller warned account will be blocked immediately unless verified right now')"
            ),
            height=90,
            key="ta_reason",
        )

        submitted = st.form_submit_button("Analyse Transaction")

    if submitted:
        customer_history = get_customer_history(analysis_customer)
        customer_profile = calculate_behaviour_profile(analysis_customer)
        result = analyse_transaction(
            customer_profile=customer_profile,
            payment_amount=payment_amount,
            payee=payee,
            payment_time=payment_time.strftime("%H:%M"),
            session_behaviour=session_behaviour,
            payment_reason=payment_reason,
            customer_history=customer_history,
        )
        st.session_state["last_analysis_result"] = result

    if "last_analysis_result" in st.session_state:
        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
        last_result = st.session_state["last_analysis_result"]
        render_risk_result_visualisation(last_result)

        if str(last_result.get("risk_category", "")).lower() == "high":
            st.markdown("<div style='height: 0.85rem;'></div>", unsafe_allow_html=True)
            st.button(
                "Start Safety Verification",
                key="start_safety_verification_btn",
                on_click=_activate_safety_verification,
            )
    else:
        st.markdown(
            """
<div class="placeholder-banner">
    Enter transaction details above and click <strong>Analyse Transaction</strong> to compare
    the transfer against the customer's synthetic history and inspect coercion risk indicators.
</div>
            """,
            unsafe_allow_html=True,
        )


def render_customer_history_section(selected_customer: str) -> None:
    """Render the selected customer's behaviour profile cards and transaction table."""
    profile = calculate_behaviour_profile(selected_customer)
    history_df = get_customer_history(selected_customer)

    st.markdown(
        f'<div class="section-heading">👤 Customer History &mdash; {html.escape(profile["customer_name"])}</div>',
        unsafe_allow_html=True,
    )

    # Normal behaviour summary card
    st.markdown(
        f"""
<div class="glass-card" style="margin-bottom: 1rem;">
    <div class="card-tag">{html.escape(profile["customer_id"])} &bull; {html.escape(profile["segment"])}</div>
    <div class="card-title">🧭 Normal Transaction Behaviour Profile</div>
    <p class="card-body">{html.escape(profile["normal_behaviour"])}</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    # 4 metric/behaviour cards
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        st.markdown(
            f"""
<div class="glass-card">
    <div class="metric-label">Average Amount</div>
    <div class="metric-value">₹{profile["average_amount"]:,.2f}</div>
    <div class="metric-sub">Synthetic baseline mean</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
<div class="glass-card">
    <div class="metric-label">Previous Transactions</div>
    <div class="metric-value">{profile["transaction_count"]}</div>
    <div class="metric-sub">Recorded history items</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
<div class="glass-card">
    <div class="metric-label">Usual Timing</div>
    <div class="metric-value" style="font-size: 1.05rem;">{html.escape(profile["usual_timing"])}</div>
    <div class="metric-sub">Expected activity window</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        payee_pills = "".join(
            f'<span class="payee-pill">{html.escape(p)}</span>'
            for p in profile["familiar_payees"]
        )
        st.markdown(
            f"""
<div class="glass-card">
    <div class="metric-label">Familiar Payees ({len(profile["familiar_payees"])})</div>
    <div class="pill-wrap">{payee_pills}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">📑 Previous Synthetic Transactions</div>',
        unsafe_allow_html=True,
    )

    # Build clean glassmorphism HTML table from Pandas DataFrame
    rows_html = []
    for _, row in history_df.iterrows():
        rows_html.append(
            "<tr>"
            f"<td>{html.escape(str(row['date']))}</td>"
            f"<td>{html.escape(str(row['time']))}</td>"
            f"<td><strong>{html.escape(str(row['payee']))}</strong></td>"
            f"<td>{html.escape(str(row['category']))}</td>"
            f"<td><span class='channel-badge'>{html.escape(str(row['channel']))}</span></td>"
            f"<td class='amount-cell'>₹{float(row['amount']):,.2f}</td>"
            "</tr>"
        )

    table_html = (
        '<div class="table-shell">'
        '<table class="safepay-table">'
        "<thead><tr>"
        "<th>Date</th>"
        "<th>Time</th>"
        "<th>Payee</th>"
        "<th>Category</th>"
        "<th>Channel</th>"
        "<th>Amount</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table>"
        "</div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def evaluate_verification_answers(
    voluntary: str,
    pressured: str,
    remote_guided: str,
    comfortable: str,
) -> dict:
    """Compute an updated calm safety recommendation from verification answers."""
    if voluntary == "No" or pressured == "Yes" or remote_guided == "Yes":
        return {
            "level": "High",
            "title": "Stop or Delay Payment Recommended",
            "badge": "Coercion / Pressure Reported",
            "message": (
                "Because pressure, non-voluntary intent, or remote guidance was reported, "
                "we strongly recommend stopping or delaying this payment right now. "
                "Step away from any active phone call or screen-sharing session and speak "
                "with a trusted family member or official support before transferring funds."
            ),
        }

    if comfortable == "No":
        return {
            "level": "Medium",
            "title": "Additional Verification Recommended",
            "badge": "User Unsure — Pause & Check",
            "message": (
                "Since you do not feel completely comfortable proceeding, pause this payment "
                "and perform additional verification. Confirm the recipient's identity and "
                "reason independently through a trusted contact number before continuing."
            ),
        }

    return {
        "level": "Low",
        "title": "Normal Safety Confirmation",
        "badge": "No Pressure Reported",
        "message": (
            "No pressure or remote guidance was reported, and you confirmed this payment is "
            "voluntary. As a normal safety habit, double-check the payee name and amount "
            "one last time before choosing whether to proceed."
        ),
    }


def render_safety_verification_section() -> None:
    """Render the simulated Safety Verification screen and dynamic recommendation."""
    st.markdown(
        '<div class="section-heading">✅ Safety Verification &mdash; Guided Coercion Check</div>',
        unsafe_allow_html=True,
    )

    last_result = st.session_state.get("last_analysis_result")
    if last_result:
        comp = last_result.get("baseline_comparison", {})
        cat = str(last_result.get("risk_category", "Low"))
        palette = _get_risk_palette(cat)
        st.markdown(
            f"""
<div class="glass-card" style="margin-bottom: 1rem; border-color: {palette["border"]};">
    <div class="card-tag" style="color: {palette["accent_soft"]}; background: {palette["bg"]}; border-color: {palette["border"]};">
        Active Transaction Context &bull; {html.escape(cat)} Risk ({int(last_result["risk_score"])}/100)
    </div>
    <div class="card-title">{palette["icon"]} Reviewing Transfer for {html.escape(str(comp.get("customer_name", "Selected Customer")))}</div>
    <p class="card-body">
        Answer the four calm reflection questions below. SafePay AI will update the safety
        recommendation based on your responses. <strong>Simulation only</strong> &mdash; no real
        phone calls are made and no bank connection exists.
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div class="placeholder-banner">
    <strong>Simulated Verification Check:</strong> Run a scan in <strong>Transaction Analysis</strong>
    first to attach transaction context, or test the four verification questions below right away.
    <em>Simulation only — no real phone calls or bank connections.</em>
</div>
            """,
            unsafe_allow_html=True,
        )

    col_q, col_out = st.columns([1.15, 1], gap="medium")

    with col_q:
        st.markdown(
            """
<div class="glass-card" style="margin-bottom: 0.75rem;">
    <div class="card-tag">Calm Self-Check</div>
    <div class="card-title">🛡️ Verification Questions</div>
    <p class="card-body">Take a brief pause and answer honestly with Yes or No.</p>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="verify-question-label">1. Is this payment voluntary?</div>',
            unsafe_allow_html=True,
        )
        q1 = st.radio(
            "1. Is this payment voluntary?",
            options=["Yes", "No"],
            index=0,
            horizontal=True,
            key="sv_voluntary",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="verify-question-label">2. Is anyone pressuring you to make this payment?</div>',
            unsafe_allow_html=True,
        )
        q2 = st.radio(
            "2. Is anyone pressuring you to make this payment?",
            options=["Yes", "No"],
            index=1,
            horizontal=True,
            key="sv_pressured",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="verify-question-label">3. Is someone guiding you remotely?</div>',
            unsafe_allow_html=True,
        )
        q3 = st.radio(
            "3. Is someone guiding you remotely?",
            options=["Yes", "No"],
            index=1,
            horizontal=True,
            key="sv_remote",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="verify-question-label">4. Do you feel comfortable proceeding?</div>',
            unsafe_allow_html=True,
        )
        q4 = st.radio(
            "4. Do you feel comfortable proceeding?",
            options=["Yes", "No"],
            index=0,
            horizontal=True,
            key="sv_comfortable",
            label_visibility="collapsed",
        )

    outcome = evaluate_verification_answers(q1, q2, q3, q4)
    out_palette = _get_risk_palette(outcome["level"])

    with col_out:
        st.markdown(
            f"""
<div class="glass-card" style="border-color: {out_palette["border"]}; box-shadow: 0 14px 34px {out_palette["glow"]};">
    <div class="card-tag" style="color: {out_palette["accent_soft"]}; background: {out_palette["bg"]}; border-color: {out_palette["border"]};">
        {html.escape(outcome["badge"])}
    </div>
    <div class="card-title" style="font-size: 1.18rem;">{out_palette["icon"]} {html.escape(outcome["title"])}</div>
    <p class="card-body" style="font-size: 0.96rem; color: #f8fafc; margin-top: 0.5rem;">
        {html.escape(outcome["message"])}
    </p>
    <div class="risk-disclaimer" style="margin-top: 1.1rem;">
        <strong>Responses Summary:</strong><br/>
        &bull; Voluntary: <strong>{html.escape(q1)}</strong> &nbsp;|&nbsp;
        Pressured: <strong>{html.escape(q2)}</strong><br/>
        &bull; Remote Guidance: <strong>{html.escape(q3)}</strong> &nbsp;|&nbsp;
        Comfortable: <strong>{html.escape(q4)}</strong>
    </div>
    <p class="card-body" style="margin-top: 0.9rem; font-size: 0.82rem; color: #94a3b8;">
        Simulation only &mdash; no real phone calls, no bank connection, and no real payment execution.
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Entry point for the SafePay AI Streamlit dashboard."""
    inject_custom_css()
    selected_customer = render_sidebar()
    render_header()

    if "nav_section" not in st.session_state:
        st.session_state["nav_section"] = "Overview"

    active_section = st.radio(
        "Navigation",
        options=[
            "Overview",
            "Transaction Analysis",
            "Customer History",
            "Safety Verification",
        ],
        horizontal=True,
        key="nav_section",
        label_visibility="collapsed",
    )

    if active_section == "Overview":
        render_overview_section(selected_customer)
    elif active_section == "Transaction Analysis":
        render_transaction_analysis_section(selected_customer)
    elif active_section == "Customer History":
        render_customer_history_section(selected_customer)
    elif active_section == "Safety Verification":
        render_safety_verification_section()


if __name__ == "__main__":
    main()
