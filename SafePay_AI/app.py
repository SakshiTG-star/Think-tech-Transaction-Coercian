"""SafePay AI — Trust Before Transfer.

Streamlit prototype dashboard for detecting possible transaction coercion and
scam intent by analysing synthetic customer behaviour and transaction context.
"""

import datetime
import html
import math
import streamlit as st

from landing import show_landing

if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    show_landing()
    st.stop()

from customer_data import (
    DEFAULT_DEMO_WALLET_BALANCE,
    calculate_behaviour_profile,
    get_customer_history,
    get_customer_names,
    record_demo_transaction,
)
from risk_engine import (
    analyse_transaction,
    get_engine_status,
    run_ml_transaction_analysis,
)


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

/* Paytm-like Demo Payment & Receipt Cards */
.paytm-shell {
    background: linear-gradient(145deg, rgba(11, 31, 64, 0.76) 0%, rgba(8, 38, 58, 0.68) 100%);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 20px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 14px 34px rgba(2, 8, 23, 0.48);
    backdrop-filter: blur(16px);
}

.paytm-top-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.paytm-upi-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #7dd3fc;
    background: rgba(2, 132, 199, 0.22);
    border: 1px solid rgba(56, 189, 248, 0.42);
}

.receipt-card {
    background: linear-gradient(145deg, rgba(10, 44, 54, 0.78) 0%, rgba(12, 27, 54, 0.75) 100%);
    border: 1px solid rgba(45, 212, 191, 0.55);
    border-radius: 22px;
    padding: 1.6rem 1.75rem;
    box-shadow: 0 16px 40px rgba(20, 184, 166, 0.2);
    backdrop-filter: blur(16px);
    margin-bottom: 1rem;
}

.receipt-amount {
    font-size: 2.2rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 0.35rem 0;
}

.receipt-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 0.85rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(148, 163, 184, 0.18);
}

.receipt-kv-label {
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
    font-weight: 600;
}

.receipt-kv-val {
    font-size: 0.94rem;
    font-weight: 650;
    color: #f1f5f9;
    margin-top: 0.18rem;
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
        metrics = engine_info.get("metrics", {})
        acc_pct = metrics.get("accuracy", 0.0) * 100
        f1_pct = metrics.get("f1_score", 0.0) * 100
        st.markdown("---")
        st.markdown("#### System Scope & ML Model")
        st.info(
            f"**Engine:** {engine_info['engine_name']}\n\n"
            f"**Test Accuracy:** {acc_pct:.1f}% | **F1:** {f1_pct:.1f}%\n\n"
            f"{engine_info.get('disclaimer', '')}\n\n"
            "No real UPI, bank connection, PINs, OTPs, or phone calls."
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
            <span class="compare-chip">ML Prediction: <strong>{html.escape("Potentially Suspicious (1)" if result.get("prediction", 0) == 1 else "Normal (0)")}</strong></span>
            <span class="compare-chip">Suspicious Probability: <strong>{float(result.get("suspicious_probability", score)):.1f}%</strong></span>
            <span class="compare-chip">Customer: <strong>{html.escape(str(comparison.get("customer_name", "")))}</strong></span>
            <span class="compare-chip">Historical Avg: <strong>₹{avg_disp:,.2f}</strong></span>
            <span class="compare-chip">Recipient: <strong>{html.escape(payee_status)}</strong></span>
            <span class="compare-chip">Time: <strong>{html.escape(tx_time_disp)}</strong> (Usual: {html.escape(usual_disp)})</span>
        </div>
        <div class="risk-disclaimer">
            Risk score represents the presence of possible coercion indicators. It is not proof of fraud.
            {html.escape(str(result.get("prototype_disclaimer", "")))}
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
        st.session_state["last_analysis_inputs"] = {
            "customer_name": analysis_customer,
            "payment_amount": float(payment_amount),
            "payee": payee,
            "payment_time": payment_time.strftime("%H:%M"),
            "session_behaviour": session_behaviour,
            "payment_reason": payment_reason,
        }

    if "last_analysis_result" in st.session_state:
        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
        last_result = st.session_state["last_analysis_result"]
        render_risk_result_visualisation(last_result)

        if last_result.get("is_suspicious") or str(last_result.get("risk_category", "")).lower() == "high":
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


def run_ml_verification_update(
    customer_name: str,
    payment_amount: float,
    payee: str,
    upi_id: str,
    payment_time: str,
    session_behaviour: str,
    payment_reason: str,
    pressured: str,
    remote_guided: str,
    receiver_verified: str,
    feels_safe: str,
) -> dict:
    """Re-run the trained LogisticRegression model using safety verification answers as features."""
    profile = calculate_behaviour_profile(customer_name)
    history_df = get_customer_history(customer_name)

    return run_ml_transaction_analysis(
        customer_profile=profile,
        payment_amount=payment_amount,
        payee=payee,
        upi_id=upi_id,
        payment_time=payment_time,
        session_behaviour=session_behaviour,
        payment_reason=payment_reason,
        customer_history=history_df,
        user_reported_pressure=1 if pressured == "Yes" else 0,
        remote_guidance_indicator=1 if remote_guided == "Yes" else 0,
        receiver_verified=1 if receiver_verified == "Yes" else 0,
        feels_safe=1 if feels_safe == "Yes" else 0,
    )


def render_safety_verification_section() -> None:
    """Render the simulated Safety Verification screen backed by the trained ML model."""
    st.markdown(
        '<div class="section-heading">✅ Safety Verification &mdash; ML-Updated Coercion Check</div>',
        unsafe_allow_html=True,
    )

    last_result = st.session_state.get("last_analysis_result")
    last_inputs = st.session_state.get("last_analysis_inputs")
    if last_result and last_inputs:
        cat = str(last_result.get("risk_category", "Low"))
        palette = _get_risk_palette(cat)
        st.markdown(
            f"""
<div class="glass-card" style="margin-bottom: 1rem; border-color: {palette["border"]};">
    <div class="card-tag" style="color: {palette["accent_soft"]}; background: {palette["bg"]}; border-color: {palette["border"]};">
        Initial ML Prediction &bull; {html.escape(cat)} Risk ({float(last_result.get("suspicious_probability", last_result["risk_score"])):.1f}%)
    </div>
    <div class="card-title">{palette["icon"]} Reviewing Transfer for {html.escape(last_inputs["customer_name"])}</div>
    <p class="card-body">
        Answer the four safety questions below. Your responses are fed into the trained
        <strong>Scikit-learn LogisticRegression</strong> model as additional features to compute an
        updated prediction. <strong>Simulation only</strong> &mdash; no real calls, banks, PINs, or OTPs.
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div class="placeholder-banner">
    <strong>Simulated ML Verification Check:</strong> Run a scan in <strong>Transaction Analysis</strong>
    or <strong>Send Money</strong> first, or test how the four verification answers update the
    <strong>LogisticRegression</strong> prediction below. <em>Uses synthetic training data; simulation only.</em>
</div>
            """,
            unsafe_allow_html=True,
        )
        default_customer = get_customer_names()[0]
        last_inputs = {
            "customer_name": default_customer,
            "payment_amount": 15000.0,
            "payee": "Unverified Receiver",
            "payment_time": "22:30",
            "session_behaviour": "Normal & Calm Session",
            "payment_reason": "Payment verification check",
        }

    col_q, col_out = st.columns([1.15, 1], gap="medium")

    with col_q:
        st.markdown(
            """
<div class="glass-card" style="margin-bottom: 0.75rem;">
    <div class="card-tag">Additional ML Features</div>
    <div class="card-title">🛡️ Safety Verification Questions</div>
    <p class="card-body">Your answers feed directly into the trained LogisticRegression model.</p>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="verify-question-label">1. Is someone pressuring you to make this payment?</div>',
            unsafe_allow_html=True,
        )
        q1 = st.radio(
            "1. Is someone pressuring you to make this payment?",
            options=["Yes", "No"],
            index=1,
            horizontal=True,
            key="sv_pressured",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="verify-question-label">2. Is someone guiding you remotely?</div>',
            unsafe_allow_html=True,
        )
        q2 = st.radio(
            "2. Is someone guiding you remotely?",
            options=["Yes", "No"],
            index=1,
            horizontal=True,
            key="sv_remote",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="verify-question-label">3. Have you personally verified the receiver?</div>',
            unsafe_allow_html=True,
        )
        q3 = st.radio(
            "3. Have you personally verified the receiver?",
            options=["Yes", "No"],
            index=0,
            horizontal=True,
            key="sv_verified",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="verify-question-label">4. Do you feel safe making this payment?</div>',
            unsafe_allow_html=True,
        )
        q4 = st.radio(
            "4. Do you feel safe making this payment?",
            options=["Yes", "No"],
            index=0,
            horizontal=True,
            key="sv_safe",
            label_visibility="collapsed",
        )

    updated = run_ml_verification_update(
        customer_name=last_inputs["customer_name"],
        payment_amount=last_inputs["payment_amount"],
        payee=last_inputs["payee"],
        upi_id="",
        payment_time=last_inputs["payment_time"],
        session_behaviour=last_inputs["session_behaviour"],
        payment_reason=last_inputs["payment_reason"],
        pressured=q1,
        remote_guided=q2,
        receiver_verified=q3,
        feels_safe=q4,
    )
    out_palette = _get_risk_palette(updated["risk_category"])
    pred_label = "Potentially Suspicious (1)" if updated["prediction"] == 1 else "Normal / Safe (0)"

    with col_out:
        st.markdown(
            f"""
<div class="glass-card" style="border-color: {out_palette["border"]}; box-shadow: 0 14px 34px {out_palette["glow"]};">
    <div class="card-tag" style="color: {out_palette["accent_soft"]}; background: {out_palette["bg"]}; border-color: {out_palette["border"]};">
        Updated ML Prediction &bull; {html.escape(updated["risk_category"])} Risk
    </div>
    <div class="card-title" style="font-size: 1.18rem;">{out_palette["icon"]} {html.escape(pred_label)} &mdash; {updated["suspicious_probability"]:.1f}%</div>
    <p class="card-body" style="font-size: 0.96rem; color: #f8fafc; margin-top: 0.5rem;">
        {html.escape(updated["recommended_action"])}
    </p>
    <div class="risk-disclaimer" style="margin-top: 1.1rem;">
        <strong>Updated Model Inputs:</strong><br/>
        &bull; Pressured: <strong>{html.escape(q1)}</strong> &nbsp;|&nbsp;
        Remote Guidance: <strong>{html.escape(q2)}</strong><br/>
        &bull; Receiver Verified: <strong>{html.escape(q3)}</strong> &nbsp;|&nbsp;
        Feels Safe: <strong>{html.escape(q4)}</strong>
    </div>
    <p class="card-body" style="margin-top: 0.9rem; font-size: 0.82rem; color: #94a3b8;">
        {html.escape(updated.get("prototype_disclaimer", ""))}
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )


def _open_customer_history_tab() -> None:
    """Switch active navigation tab to Customer History."""
    st.session_state["nav_section"] = "Customer History"


def _get_demo_wallet_balance(customer_name: str) -> float:
    """Return the fictional DEMO wallet balance for the selected customer."""
    wallets = st.session_state.setdefault("demo_wallets", {})
    if customer_name not in wallets:
        wallets[customer_name] = float(DEFAULT_DEMO_WALLET_BALANCE)
    return float(wallets[customer_name])


def _reset_send_money() -> None:
    """Reset the Paytm-like Send Money demo workflow back to the input form."""
    st.session_state["sm_stage"] = "form"
    st.session_state["sm_show_verify"] = False
    st.session_state.pop("sm_payload", None)
    st.session_state.pop("sm_analysis", None)
    st.session_state.pop("sm_updated_analysis", None)
    st.session_state.pop("sm_receipt", None)


def _render_recent_demo_transactions(customer_name: str) -> None:
    """Render recent DEMO transactions table cleanly inside the Send Money section."""
    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">🧾 Recent Demo Transactions <span class="channel-badge">DEMO ONLY</span></div>',
        unsafe_allow_html=True,
    )

    session_demos = [
        tx
        for tx in st.session_state.get("recent_demo_transactions", [])
        if tx.get("customer_name") == customer_name
    ]
    history_df = get_customer_history(customer_name)

    rows_html = []
    # Show newly confirmed DEMO wallet transactions first
    for tx in reversed(session_demos):
        rows_html.append(
            "<tr>"
            f"<td><span class='channel-badge'>DEMO</span> {html.escape(tx['txn_id'])}</td>"
            f"<td>{html.escape(tx['date'])} {html.escape(tx['time'])}</td>"
            f"<td><strong>{html.escape(tx['payee'])}</strong> <span style='color:#94a3b8;font-size:0.8rem;'>({html.escape(tx['receiver_id'])})</span></td>"
            f"<td>{html.escape(tx['category'])}</td>"
            f"<td class='amount-cell'>₹{float(tx['amount']):,.2f}</td>"
            "</tr>"
        )

    # Also show recent synthetic baseline transactions labeled as DEMO
    for _, row in history_df.tail(4).iloc[::-1].iterrows():
        rows_html.append(
            "<tr>"
            "<td><span class='channel-badge'>DEMO BASELINE</span></td>"
            f"<td>{html.escape(str(row['date']))} {html.escape(str(row['time']))}</td>"
            f"<td><strong>{html.escape(str(row['payee']))}</strong></td>"
            f"<td>{html.escape(str(row['category']))}</td>"
            f"<td class='amount-cell'>₹{float(row['amount']):,.2f}</td>"
            "</tr>"
        )

    st.markdown(
        '<div class="table-shell">'
        '<table class="safepay-table">'
        "<thead><tr>"
        "<th>Demo Reference</th>"
        "<th>Date &amp; Time</th>"
        "<th>Receiver</th>"
        "<th>Category</th>"
        "<th>Amount</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_send_money_section(selected_customer: str) -> None:
    """Render Paytm-like Send Money demo feature protected by the trained ML model."""
    st.markdown(
        '<div class="section-heading">💸 Send Money &mdash; Demo Wallet Checkout</div>',
        unsafe_allow_html=True,
    )

    if "sm_stage" not in st.session_state:
        st.session_state["sm_stage"] = "form"

    # Reset checkout step cleanly if user switches synthetic customer in sidebar
    if st.session_state.get("sm_active_customer") != selected_customer:
        st.session_state["sm_active_customer"] = selected_customer
        _reset_send_money()

    profile = calculate_behaviour_profile(selected_customer)
    wallet_balance = _get_demo_wallet_balance(selected_customer)
    stage = st.session_state["sm_stage"]

    # Top Paytm-like DEMO Wallet Balance Banner
    st.markdown(
        f"""
<div class="paytm-shell">
    <div class="paytm-top-bar">
        <div>
            <div class="card-title" style="margin-bottom: 0.2rem;">
                💳 SafePay Demo Wallet <span class="channel-badge" style="margin-left:0.35rem;">DEMO</span>
            </div>
            <p class="card-body">
                Sender: <strong>{html.escape(profile["customer_name"])}</strong>
                ({html.escape(profile["customer_id"])}) &bull; Baseline Avg:
                <strong>₹{profile["average_amount"]:,.2f}</strong>
            </p>
        </div>
        <div style="text-align: right;">
            <div class="metric-label" style="margin-bottom: 0.15rem;">DEMO Wallet Balance</div>
            <div class="metric-value" style="color: #5eead4;">₹{wallet_balance:,.2f}</div>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Stage 1: Send Money Input Form
    # ------------------------------------------------------------------
    if stage == "form":
        with st.form("send_money_form", clear_on_submit=False):
            r1, r2, r3 = st.columns([1.15, 1.15, 0.9], gap="medium")
            with r1:
                receiver_name = st.text_input(
                    "Receiver Name",
                    value="FreshMart Groceries",
                    placeholder="e.g., FreshMart Groceries or Demo Store",
                    key="sm_receiver_name",
                )
            with r2:
                receiver_id = st.text_input(
                    "Fictional Receiver ID",
                    value="safeuser101",
                    placeholder="e.g., safeuser101 or demo.receiver202",
                    key="sm_receiver_id",
                )
            with r3:
                pay_amount = st.number_input(
                    "Payment Amount (₹)",
                    min_value=1.0,
                    max_value=1000000.0,
                    value=min(1800.0, max(1.0, wallet_balance)),
                    step=250.0,
                    key="sm_amount",
                )

            c1, c2, c3 = st.columns([0.85, 1.05, 1.3], gap="medium")
            with c1:
                pay_time = st.time_input(
                    "Payment Time",
                    value=datetime.time(14, 30),
                    key="sm_time",
                )
            with c2:
                sm_session = st.selectbox(
                    "Session Behaviour",
                    options=[
                        "Normal & Calm Session",
                        "Hurried / Rushed Navigation",
                        "Hesitant / Repeated Input Edits",
                        "Possible Remote-Access Tool Hint (Screen Share / AnyDesk)",
                        "Hurried Session + Remote-Access Hint",
                    ],
                    index=0,
                    key="sm_session",
                )
            with c3:
                pay_purpose = st.text_input(
                    "Payment Message or Purpose",
                    value="Monthly groceries and vegetables",
                    placeholder="Enter payment message (English, Hindi, or Kannada)",
                    key="sm_purpose",
                )

            continue_clicked = st.form_submit_button("Continue to Payment")

        st.caption(
            "DEMO mode only: Synthetic receiver IDs only (e.g., safeuser101, demo.receiver202). "
            "No real banks, UPI, PINs, OTPs, or payment gateways."
        )

        if continue_clicked:
            clean_receiver = receiver_name.strip()
            clean_receiver_id = receiver_id.strip()
            if not clean_receiver:
                st.warning("Please enter a synthetic Receiver Name before continuing.")
            elif not clean_receiver_id:
                st.warning("Please enter a Fictional Receiver ID (e.g., `safeuser101` or `demo.receiver202`).")
            elif float(pay_amount) > wallet_balance:
                st.warning(
                    f"Insufficient DEMO wallet balance (available: ₹{wallet_balance:,.2f}). "
                    "Please enter a smaller demo amount."
                )
            else:
                history_df = get_customer_history(selected_customer)
                analysis = run_ml_transaction_analysis(
                    customer_profile=profile,
                    payment_amount=pay_amount,
                    payee=clean_receiver,
                    upi_id=clean_receiver_id,
                    payment_time=pay_time.strftime("%H:%M"),
                    session_behaviour=sm_session,
                    payment_reason=pay_purpose,
                    customer_history=history_df,
                )
                st.session_state["sm_payload"] = {
                    "customer_name": selected_customer,
                    "receiver_name": clean_receiver,
                    "receiver_id": clean_receiver_id,
                    "amount": float(pay_amount),
                    "payment_time": pay_time.strftime("%H:%M"),
                    "session_behaviour": sm_session,
                    "payment_purpose": pay_purpose.strip() or "Demo wallet transfer",
                }
                st.session_state["sm_analysis"] = analysis
                st.session_state.pop("sm_updated_analysis", None)
                st.session_state["sm_show_verify"] = bool(analysis["prediction"] == 1)
                st.session_state["sm_stage"] = "review"
                st.rerun()

    # ------------------------------------------------------------------
    # Stage 2: Automatic ML Risk Analysis + Safety Verification + Actions
    # ------------------------------------------------------------------
    elif stage == "review":
        payload = st.session_state["sm_payload"]
        analysis = st.session_state["sm_analysis"]
        show_verify = st.session_state.get("sm_show_verify", False)
        active_analysis = st.session_state.get("sm_updated_analysis", analysis)

        if analysis["prediction"] == 1 or show_verify:
            if analysis["prediction"] == 1:
                palette_warn = _get_risk_palette(analysis["risk_category"])
                st.markdown(
                    f"""
<div class="glass-card" style="border-color: {palette_warn["border"]}; box-shadow: 0 14px 34px {palette_warn["glow"]}; margin-bottom: 1rem;">
    <div class="card-tag" style="color: {palette_warn["accent_soft"]}; background: {palette_warn["bg"]}; border-color: {palette_warn["border"]};">
        {palette_warn["icon"]} Suspicious Transaction Warning &bull; ML Prediction: Potentially Suspicious
    </div>
    <div class="card-title" style="font-size: 1.18rem;">
        Safety Check Required Before Demo Payment Confirmation
    </div>
    <p class="card-body">
        The trained Scikit-learn LogisticRegression model flagged this transfer with a suspicious
        probability of <strong>{analysis["suspicious_probability"]:.1f}%</strong>. Answer the four
        safety verification questions below and click <strong>Update ML Prediction</strong>.
    </p>
</div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
<div class="glass-card" style="margin-bottom: 0.75rem;">
    <div class="card-tag">Verify Receiver &amp; Coercion Context</div>
    <div class="card-title">🛡️ Safety Verification Questions</div>
    <p class="card-body">Your answers are passed as additional features into the trained LogisticRegression model.</p>
</div>
                """,
                unsafe_allow_html=True,
            )

            vq1, vq2 = st.columns(2, gap="medium")
            with vq1:
                st.markdown('<div class="verify-question-label">1. Is someone pressuring you to make this payment?</div>', unsafe_allow_html=True)
                q_pressured = st.radio("sm_q_pressured", ["Yes", "No"], index=1, horizontal=True, key="sm_q_pressured", label_visibility="collapsed")

                st.markdown('<div class="verify-question-label">2. Is someone guiding you remotely?</div>', unsafe_allow_html=True)
                q_remote = st.radio("sm_q_remote", ["Yes", "No"], index=1, horizontal=True, key="sm_q_remote", label_visibility="collapsed")
            with vq2:
                st.markdown('<div class="verify-question-label">3. Have you verified the receiver?</div>', unsafe_allow_html=True)
                q_verified = st.radio(
                    "sm_q_verified",
                    ["Yes", "No"],
                    index=0 if analysis["baseline_comparison"]["is_familiar_payee"] else 1,
                    horizontal=True,
                    key="sm_q_verified",
                    label_visibility="collapsed",
                )

                st.markdown('<div class="verify-question-label">4. Do you feel safe making this payment?</div>', unsafe_allow_html=True)
                q_safe = st.radio("sm_q_safe", ["Yes", "No"], index=0, horizontal=True, key="sm_q_safe", label_visibility="collapsed")

            if st.button("Update ML Prediction with Answers", key="sm_update_ml_btn"):
                st.session_state["sm_updated_analysis"] = run_ml_verification_update(
                    customer_name=payload["customer_name"],
                    payment_amount=payload["amount"],
                    payee=payload["receiver_name"],
                    upi_id=payload["receiver_id"],
                    payment_time=payload["payment_time"],
                    session_behaviour=payload["session_behaviour"],
                    payment_reason=payload["payment_purpose"],
                    pressured=q_pressured,
                    remote_guided=q_remote,
                    receiver_verified=q_verified,
                    feels_safe=q_safe,
                )
                st.rerun()

        palette = _get_risk_palette(active_analysis["risk_category"])
        pred_label = (
            "Potentially Suspicious (1)" if active_analysis["prediction"] == 1 else "Normal / Safe (0)"
        )
        ml_feats = active_analysis.get("ml_features", {})

        # Pre-confirmation ML summary card showing all required fields
        st.markdown(
            f"""
<div class="glass-card" style="border-color: {palette["border"]}; margin: 0.75rem 0 1rem 0;">
    <div class="card-tag" style="color: {palette["accent_soft"]}; background: {palette["bg"]}; border-color: {palette["border"]};">
        Trained Scikit-learn ML Risk Analysis &bull; {html.escape(active_analysis["risk_category"])} Risk
    </div>
    <div class="card-title" style="font-size: 1.18rem;">
        {palette["icon"]} {html.escape(pred_label)} &mdash; Suspicious Probability: {active_analysis["suspicious_probability"]:.1f}%
    </div>
    <div class="receipt-grid">
        <div>
            <div class="receipt-kv-label">Receiver Name &amp; Fictional ID</div>
            <div class="receipt-kv-val">{html.escape(payload["receiver_name"])} ({html.escape(payload["receiver_id"])})</div>
        </div>
        <div>
            <div class="receipt-kv-label">Payment Amount</div>
            <div class="receipt-kv-val">₹{payload["amount"]:,.2f}</div>
        </div>
        <div>
            <div class="receipt-kv-label">ML Prediction &amp; Category</div>
            <div class="receipt-kv-val">{html.escape(pred_label)} &bull; {html.escape(active_analysis["risk_category"])}</div>
        </div>
        <div>
            <div class="receipt-kv-label">Behavioral Factors Considered</div>
            <div class="receipt-kv-val">
                Ratio: {ml_feats.get("amount_deviation_ratio", 1.0):.2f}x |
                New Receiver: {"Yes" if ml_feats.get("new_receiver_indicator", 0) >= 0.5 else "No"} |
                Unusual Time: {"Yes" if ml_feats.get("unusual_transaction_time", 0) >= 0.5 else "No"}
            </div>
        </div>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        render_risk_result_visualisation(active_analysis)
        st.markdown("<div style='height: 0.9rem;'></div>", unsafe_allow_html=True)

        # Required 3 buttons after risk analysis: Cancel Payment, Verify Receiver, Continue with Demo Payment
        b1, b2, b3 = st.columns(3, gap="medium")
        with b1:
            if st.button("Cancel Payment", key="sm_cancel_btn"):
                st.session_state["sm_stage"] = "cancelled"
                st.rerun()
        with b2:
            if st.button("Verify Receiver", key="sm_verify_btn"):
                st.session_state["sm_show_verify"] = True
                st.rerun()
        with b3:
            if st.button("Continue with Demo Payment", key="sm_continue_demo_btn"):
                if payload["amount"] > _get_demo_wallet_balance(payload["customer_name"]):
                    st.warning("Insufficient DEMO wallet balance for this transfer.")
                else:
                    # Deduct from fictional DEMO wallet balance only on confirmation
                    st.session_state["demo_wallets"][payload["customer_name"]] = round(
                        _get_demo_wallet_balance(payload["customer_name"]) - payload["amount"],
                        2,
                    )
                    receipt = record_demo_transaction(
                        customer_name=payload["customer_name"],
                        payee=payload["receiver_name"],
                        amount=payload["amount"],
                        receiver_id=payload["receiver_id"],
                        category="Demo Wallet Transfer",
                        channel="SafePay Demo Wallet",
                        time_str=payload["payment_time"],
                    )
                    receipt["risk_score"] = active_analysis["risk_score"]
                    receipt["risk_category"] = active_analysis["risk_category"]
                    receipt["suspicious_probability"] = active_analysis["suspicious_probability"]
                    receipt["remaining_balance"] = st.session_state["demo_wallets"][payload["customer_name"]]
                    st.session_state.setdefault("recent_demo_transactions", []).append(receipt)
                    st.session_state["sm_receipt"] = receipt
                    st.session_state["sm_stage"] = "receipt"
                    st.rerun()

    # ------------------------------------------------------------------
    # Stage 3: Payment Success Receipt
    # ------------------------------------------------------------------
    elif stage == "receipt":
        receipt = st.session_state["sm_receipt"]
        st.markdown(
            f"""
<div class="receipt-card">
    <div class="card-tag">✅ DEMO Payment Successful (Simulated)</div>
    <div class="card-title" style="font-size: 1.25rem;">SafePay Demo Payment Receipt</div>
    <div class="receipt-amount">₹{float(receipt["amount"]):,.2f}</div>
    <p class="card-body" style="color: #99f6e4;">
        DEMO wallet transfer completed for <strong>{html.escape(receipt["customer_name"])}</strong>.
        Remaining DEMO Wallet Balance: <strong>₹{float(receipt["remaining_balance"]):,.2f}</strong>.
    </p>
    <div class="receipt-grid">
        <div>
            <div class="receipt-kv-label">Fictional Reference ID</div>
            <div class="receipt-kv-val">{html.escape(receipt["txn_id"])}</div>
        </div>
        <div>
            <div class="receipt-kv-label">Receiver Name</div>
            <div class="receipt-kv-val">{html.escape(receipt["payee"])}</div>
        </div>
        <div>
            <div class="receipt-kv-label">Fictional Receiver ID</div>
            <div class="receipt-kv-val">{html.escape(receipt["receiver_id"])}</div>
        </div>
        <div>
            <div class="receipt-kv-label">Date &amp; Time</div>
            <div class="receipt-kv-val">{html.escape(receipt["date"])} &bull; {html.escape(receipt["time"])}</div>
        </div>
        <div>
            <div class="receipt-kv-label">ML Risk Assessment</div>
            <div class="receipt-kv-val">{html.escape(str(receipt["risk_category"]))} ({float(receipt["suspicious_probability"]):.1f}%)</div>
        </div>
        <div>
            <div class="receipt-kv-label">Mode</div>
            <div class="receipt-kv-val">{html.escape(receipt["channel"])} (DEMO)</div>
        </div>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        r_left, r_right = st.columns(2, gap="medium")
        with r_left:
            st.button(
                "View Updated Customer History",
                key="sm_view_history_btn",
                on_click=_open_customer_history_tab,
            )
        with r_right:
            if st.button("Send Another Demo Payment", key="sm_new_payment_btn"):
                _reset_send_money()
                st.rerun()

    # ------------------------------------------------------------------
    # Stage: Cancelled Safely (Wallet untouched)
    # ------------------------------------------------------------------
    elif stage == "cancelled":
        st.markdown(
            f"""
<div class="glass-card" style="border-color: rgba(45, 212, 191, 0.5); margin-bottom: 1rem;">
    <div class="card-tag">🛡️ Payment Cancelled</div>
    <div class="card-title">Demo Payment Cancelled Safely</div>
    <p class="card-body">
        No amount was deducted from your DEMO wallet (balance remains
        <strong>₹{wallet_balance:,.2f}</strong>) and no transaction was recorded.
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start New Demo Payment", key="sm_restart_btn"):
            _reset_send_money()
            st.rerun()

    _render_recent_demo_transactions(selected_customer)


def _enter_safepay_app() -> None:
    """Transition from the animated welcome screen into the SafePay AI dashboard."""
    st.session_state["entered_app"] = True


def render_welcome_screen() -> None:
    """Render the full-screen animated cybersecurity particle welcome screen."""
    st.markdown(
        """
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 960px !important;
    padding-top: 1.5rem !important;
}

/* Full-screen animated particle network layer */
.welcome-particles-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
    background:
        radial-gradient(circle at 20% 25%, rgba(20, 184, 166, 0.22) 0%, transparent 42%),
        radial-gradient(circle at 80% 30%, rgba(56, 189, 248, 0.20) 0%, transparent 44%),
        radial-gradient(circle at 50% 85%, rgba(14, 116, 144, 0.22) 0%, transparent 48%),
        linear-gradient(140deg, #020612 0%, #051127 52%, #062136 100%);
}

.welcome-net-svg {
    position: absolute;
    inset: -4%;
    width: 108%;
    height: 108%;
}

.net-layer-a {
    animation: driftA 18s ease-in-out infinite alternate;
    transform-origin: center;
}

.net-layer-b {
    animation: driftB 22s ease-in-out infinite alternate;
    transform-origin: center;
}

.net-layer-c {
    animation: driftC 14s ease-in-out infinite alternate;
    transform-origin: center;
}

@keyframes driftA {
    0%   { transform: translate3d(-12px, -10px, 0) scale(1); opacity: 0.78; }
    50%  { transform: translate3d(14px, 8px, 0) scale(1.02); opacity: 0.95; }
    100% { transform: translate3d(-6px, 16px, 0) scale(1.01); opacity: 0.82; }
}

@keyframes driftB {
    0%   { transform: translate3d(14px, 10px, 0) scale(1.01); opacity: 0.72; }
    50%  { transform: translate3d(-16px, -8px, 0) scale(0.99); opacity: 0.92; }
    100% { transform: translate3d(10px, -14px, 0) scale(1.02); opacity: 0.75; }
}

@keyframes driftC {
    0%   { transform: translate3d(0px, 12px, 0); opacity: 0.65; }
    100% { transform: translate3d(12px, -12px, 0); opacity: 0.95; }
}

.floating-dot {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, #99f6e4 0%, #2dd4bf 55%, transparent 100%);
    box-shadow: 0 0 14px rgba(45, 212, 191, 0.75);
    animation: floatOrb 10s ease-in-out infinite;
}

.dot-1 { width: 7px; height: 7px; top: 18%; left: 16%; animation-duration: 9s; }
.dot-2 { width: 5px; height: 5px; top: 28%; left: 82%; animation-duration: 12s; animation-delay: -2s; }
.dot-3 { width: 8px; height: 8px; top: 72%; left: 22%; animation-duration: 11s; animation-delay: -4s; }
.dot-4 { width: 6px; height: 6px; top: 68%; left: 78%; animation-duration: 13s; animation-delay: -1s; }
.dot-5 { width: 5px; height: 5px; top: 45%; left: 10%; animation-duration: 10s; animation-delay: -5s; }
.dot-6 { width: 7px; height: 7px; top: 14%; left: 56%; animation-duration: 14s; animation-delay: -3s; }

@keyframes floatOrb {
    0%, 100% { transform: translate3d(0, 0, 0) scale(1); opacity: 0.55; }
    50%      { transform: translate3d(14px, -22px, 0) scale(1.35); opacity: 1; }
}

/* Centered Welcome Glass Card */
.welcome-gate-card {
    position: relative;
    z-index: 2;
    max-width: 720px;
    margin: clamp(2.2rem, 9vh, 5.5rem) auto 1.35rem auto;
    padding: clamp(1.8rem, 4vw, 3rem) clamp(1.4rem, 4vw, 2.75rem);
    border-radius: 26px;
    text-align: center;
    background: linear-gradient(145deg, rgba(10, 25, 52, 0.72) 0%, rgba(8, 36, 54, 0.64) 100%);
    border: 1px solid rgba(45, 212, 191, 0.36);
    box-shadow:
        0 24px 60px rgba(2, 8, 23, 0.72),
        0 0 42px rgba(20, 184, 166, 0.16),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    animation: cardFadeUp 0.75s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes cardFadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

.welcome-shield-ring {
    width: 76px;
    height: 76px;
    margin: 0 auto 1.15rem auto;
    border-radius: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, rgba(20, 184, 166, 0.25), rgba(56, 189, 248, 0.2));
    border: 1px solid rgba(45, 212, 191, 0.55);
    box-shadow: 0 0 28px rgba(45, 212, 191, 0.32);
    animation: shieldPulse 3s ease-in-out infinite;
}

@keyframes shieldPulse {
    0%, 100% { box-shadow: 0 0 24px rgba(45, 212, 191, 0.28); transform: scale(1); }
    50%      { box-shadow: 0 0 38px rgba(56, 189, 248, 0.45); transform: scale(1.03); }
}

.welcome-main-title {
    margin: 0.4rem 0 0.45rem 0;
    font-size: clamp(1.9rem, 4.2vw, 2.85rem);
    font-weight: 800;
    letter-spacing: -0.025em;
    line-height: 1.12;
    background: linear-gradient(90deg, #f8fafc 0%, #bae6fd 48%, #5eead4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-main-subtitle {
    margin: 0 0 0.95rem 0;
    font-size: clamp(1.05rem, 2.2vw, 1.32rem);
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5eead4;
}

.welcome-main-desc {
    margin: 0 auto;
    max-width: 560px;
    font-size: clamp(0.95rem, 1.8vw, 1.08rem);
    line-height: 1.6;
    color: #cbd5e1;
}

/* Animated Enter SafePay AI Button */
div.stButton > button {
    position: relative;
    z-index: 2;
    background: linear-gradient(135deg, #14b8a6 0%, #0284c7 55%, #0ea5e9 100%) !important;
    background-size: 200% 200% !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
    font-weight: 750 !important;
    letter-spacing: 0.03em !important;
    padding: 0.85rem 1.8rem !important;
    border-radius: 14px !important;
    border: 1px solid rgba(94, 234, 212, 0.7) !important;
    box-shadow: 0 10px 30px rgba(20, 184, 166, 0.38) !important;
    animation: btnGlowShift 4s ease infinite !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 16px 38px rgba(45, 212, 191, 0.55) !important;
}

@keyframes btnGlowShift {
    0%, 100% { background-position: 0% 50%; box-shadow: 0 10px 28px rgba(20, 184, 166, 0.35); }
    50%      { background-position: 100% 50%; box-shadow: 0 12px 36px rgba(56, 189, 248, 0.5); }
}
</style>

<div class="welcome-particles-bg" aria-hidden="true">
    <span class="floating-dot dot-1"></span>
    <span class="floating-dot dot-2"></span>
    <span class="floating-dot dot-3"></span>
    <span class="floating-dot dot-4"></span>
    <span class="floating-dot dot-5"></span>
    <span class="floating-dot dot-6"></span>
    <svg class="welcome-net-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
        <g class="net-layer-a" stroke="rgba(45, 212, 191, 0.22)" stroke-width="1.2">
            <line x1="120" y1="160" x2="340" y2="260" />
            <line x1="340" y1="260" x2="540" y2="140" />
            <line x1="540" y1="140" x2="820" y2="210" />
            <line x1="820" y1="210" x2="1120" y2="120" />
            <line x1="1120" y1="120" x2="1320" y2="280" />
            <line x1="340" y1="260" x2="260" y2="520" />
            <line x1="260" y1="520" x2="480" y2="680" />
            <circle cx="120" cy="160" r="3.5" fill="#2dd4bf" stroke="none" />
            <circle cx="340" cy="260" r="4.5" fill="#38bdf8" stroke="none" />
            <circle cx="540" cy="140" r="3" fill="#99f6e4" stroke="none" />
            <circle cx="820" cy="210" r="4" fill="#2dd4bf" stroke="none" />
            <circle cx="1120" cy="120" r="3.5" fill="#38bdf8" stroke="none" />
            <circle cx="1320" cy="280" r="4" fill="#2dd4bf" stroke="none" />
            <circle cx="260" cy="520" r="3.5" fill="#5eead4" stroke="none" />
            <circle cx="480" cy="680" r="4" fill="#38bdf8" stroke="none" />
        </g>
        <g class="net-layer-b" stroke="rgba(56, 189, 248, 0.2)" stroke-width="1.1">
            <line x1="180" y1="740" x2="430" y2="590" />
            <line x1="430" y1="590" x2="720" y2="760" />
            <line x1="720" y1="760" x2="1040" y2="650" />
            <line x1="1040" y1="650" x2="1280" y2="770" />
            <line x1="1040" y1="650" x2="1220" y2="440" />
            <line x1="1220" y1="440" x2="960" y2="330" />
            <line x1="960" y1="330" x2="1120" y2="120" />
            <circle cx="180" cy="740" r="3.5" fill="#38bdf8" stroke="none" />
            <circle cx="430" cy="590" r="3" fill="#2dd4bf" stroke="none" />
            <circle cx="720" cy="760" r="4.5" fill="#5eead4" stroke="none" />
            <circle cx="1040" cy="650" r="4" fill="#38bdf8" stroke="none" />
            <circle cx="1280" cy="770" r="3.5" fill="#2dd4bf" stroke="none" />
            <circle cx="1220" cy="440" r="4" fill="#99f6e4" stroke="none" />
            <circle cx="960" cy="330" r="3" fill="#38bdf8" stroke="none" />
        </g>
        <g class="net-layer-c" stroke="rgba(94, 234, 212, 0.16)" stroke-width="1">
            <line x1="210" y1="360" x2="460" y2="410" />
            <line x1="980" y1="480" x2="1290" y2="540" />
            <line x1="620" y1="110" x2="680" y2="270" />
            <circle cx="210" cy="360" r="3" fill="#2dd4bf" stroke="none" />
            <circle cx="460" cy="410" r="2.8" fill="#38bdf8" stroke="none" />
            <circle cx="980" cy="480" r="3.2" fill="#2dd4bf" stroke="none" />
            <circle cx="1290" cy="540" r="3.5" fill="#38bdf8" stroke="none" />
            <circle cx="620" cy="110" r="2.8" fill="#99f6e4" stroke="none" />
            <circle cx="680" cy="270" r="3" fill="#2dd4bf" stroke="none" />
        </g>
    </svg>
</div>

<div class="welcome-gate-card">
    <div class="welcome-shield-ring">
        <svg width="38" height="38" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2.5L4.5 5.8V11.5C4.5 16.4 7.7 20.8 12 22C16.3 20.8 19.5 16.4 19.5 11.5V5.8L12 2.5Z"
                  stroke="#2dd4bf" stroke-width="1.9" fill="rgba(45, 212, 191, 0.16)"/>
            <path d="M9.2 12.1L11.1 14L15 9.9" stroke="#f8fafc" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <div class="card-tag">AI Cybersecurity &amp; FinTech Shield</div>
    <h1 class="welcome-main-title">Welcome to SafePay AI</h1>
    <div class="welcome-main-subtitle">Trust Before Transfer</div>
    <p class="welcome-main-desc">
        Your intelligent payment protection companion. Analyze transaction risks before you transfer.
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 1.15, 1])
    with center_col:
        st.button(
            "Enter SafePay AI",
            key="enter_safepay_btn",
            on_click=_enter_safepay_app,
        )


def main() -> None:
    """Entry point for the SafePay AI Streamlit dashboard."""
    inject_custom_css()

    if not st.session_state.get("entered_app", False):
        render_welcome_screen()
        return

    selected_customer = render_sidebar()
    render_header()

    if "nav_section" not in st.session_state:
        st.session_state["nav_section"] = "Overview"

    active_section = st.radio(
        "Navigation",
        options=[
            "Overview",
            "Transaction Analysis",
            "Send Money",
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
    elif active_section == "Send Money":
        render_send_money_section(selected_customer)
    elif active_section == "Customer History":
        render_customer_history_section(selected_customer)
    elif active_section == "Safety Verification":
        render_safety_verification_section()


if __name__ == "__main__":
    main()
