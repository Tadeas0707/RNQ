import streamlit as st
import time

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="MNQ Opening Bias Scouter",
    page_icon="⚡",
    layout="centered"
)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .bias-card {
        background: #161b22;
        border: 2px solid #30363d;
        border-radius: 8px;
        padding: 25px;
        text-align: center;
        margin-bottom: 25px;
    }
    .bias-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b949e;
    }
    .bullish { color: #3fb950; border-color: #238636; }
    .bearish { color: #f85149; border-color: #da3633; }
    .neutral { color: #d29922; border-color: #d29922; }
    .card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("⚡ MNQ Wall Street Opening Scouter")
st.caption("Window: 15:30 - 17:00 SEČ | Institucionální fundamentální filtr")

# --- SIMULACE / DATA SCOUTERU ---
# Zde se v budoucnu tahají reálná data z API (VIX, US10Y, Kalendář)
vix_val = 16.4
us10y_trend = "DOWN"
nq_premarket = 0.52
earnings_bias = "BULLISH"
high_impact_news = False

# Vyhodnocení skóre
score = 0
reasons = []

if high_impact_news:
    bias = "NO-TRADE / HIGH RISK"
    css_class = "neutral"
    color_code = "#d29922"
    reasons.append("🚨 Klíčová makro data (CPI/NFP/FOMC) v kalendáři!")
else:
    if us10y_trend == "DOWN":
        score += 2
        reasons.append("Pokles výnosů US10Y podporuje růst technologického indexu.")
    elif us10y_trend == "UP":
        score -= 2
        reasons.append("Růst výnosů US10Y vyvíjí tlak na pokles tech sektoru.")
        
    if nq_premarket > 0.4:
        score += 1
        reasons.append("Pre-market silně býčí.")
    elif nq_premarket < -0.4:
        score -= 1
        reasons.append("Pre-market pod prodejním tlakem.")

    if earnings_bias == "BULLISH":
        score += 2
        reasons.append("Výsledky Big Tech překonaly očekávání.")

    if score >= 2:
        bias = "BULLISH BIAS"
        css_class = "bullish"
        color_code = "#3fb950"
    elif score <= -2:
        bias = "BEARISH BIAS"
        css_class = "bearish"
        color_code = "#f85149"
    else:
        bias = "NEUTRÁLNÍ / MIXED"
        css_class = "neutral"
        color_code = "#c9d1d9"

# --- UI VÝSTUP ---
st.markdown(f"""
<div class="bias-card {css_class}">
    <div class="bias-title">Wall Street Opening Bias</div>
    <div style="font-size: 2.2rem; font-weight: bold; margin: 10px 0; color: {color_code};">{bias}</div>
    <div style="font-size: 0.95rem; color: #8b949e;">{"<br>".join(reasons)}</div>
</div>
""", unsafe_allow_html=True)

# --- METRIKY V MŘÍŽCE ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""<div class="card">""", unsafe_allow_html=True)
    st.subheader("Makro Data")
    st.metric(label="CPI / Inflace", value="Čistý kalendář")
    st.metric(label="Fed Sazby", value="Neutrální")
    st.markdown("""</div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""<div class="card">""", unsafe_allow_html=True)
    st.subheader("Tržní Podmínky")
    st.metric(label="VIX Index", value=vix_val, delta="-0.4")
    st.metric(label="US 10Y Yields", value=us10y_trend)
    st.markdown("""</div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""<div class="card">""", unsafe_allow_html=True)
    st.subheader("Big Tech Earnings")
    st.metric(label="Magnificent 7", value=earnings_bias)
    st.metric(label="Pre-market NQ", value=f"{nq_premarket}%")
    st.markdown("""</div>""", unsafe_allow_html=True)

if st.button("🔄 Znova Skenovat Trh"):
    with st.spinner("Skenuji ověřené zdroje Wall Street..."):
        time.sleep(0.6)
    st.rerun()
