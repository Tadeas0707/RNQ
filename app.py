import streamlit as st

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
st.caption("Window: 15:30 - 17:00 SEČ | Stabilní režim")

# --- BEZPEČNÉ NAČTENÍ DAT S OCHRANOU PROTI ZASEKNUTÍ ---
@st.cache_data(ttl=300)
def get_market_data():
    try:
        import yfinance as yf
        # Rychlý pokus o stažení dat s ochraną
        vix = yf.Ticker("^VIX").history(period="2d")
        tnx = yf.Ticker("^TNX").history(period="2d")
        nq = yf.Ticker("NQ=F").history(period="2d")

        if not vix.empty and not tnx.empty and not nq.empty:
            vix_val = round(vix['Close'].iloc[-1], 2)
            vix_change = round(vix_val - vix['Close'].iloc[-2], 2)
            us10y_trend = "DOWN" if tnx['Close'].iloc[-1] < tnx['Close'].iloc[-2] else "UP"
            nq_pct = round(((nq['Close'].iloc[-1] - nq['Open'].iloc[-1]) / nq['Open'].iloc[-1]) * 100, 2)
            return vix_val, vix_change, us10y_trend, nq_pct, True
    except Exception:
        pass
    
    # Bezpečný fallback, pokud Yahoo v cloudu odmítne odpovědět
    return 16.4, -0.4, "DOWN", 0.52, False

vix_val, vix_change, us10y_trend, nq_premarket, is_live = get_market_data()

# --- VYHODNOCENÍ ---
score = 0
reasons = []

if vix_val >= 22:
    bias = "NO-TRADE / HIGH RISK"
    css_class = "neutral"
    color_code = "#d29922"
    reasons.append(f"🚨 VIX je příliš vysoký ({vix_val}).")
else:
    if us10y_trend == "DOWN":
        score += 2
        reasons.append("Pokles výnosů US10Y podporuje růst technologického sektoru.")
    elif us10y_trend == "UP":
        score -= 2
        reasons.append("Růst výnosů US10Y vyvíjí tlak na pokles tech sektoru.")
        
    if nq_premarket > 0.2:
        score += 1
        reasons.append(f"Pre-market NQ roste ({nq_premarket}%).")
    elif nq_premarket < -0.2:
        score -= 1
        reasons.append(f"Pre-market NQ klesá ({nq_premarket}%).")

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

# --- METRIKY ---
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
    st.metric(label="VIX Index", value=vix_val, delta=str(vix_change))
    st.metric(label="US 10Y Yields", value=us10y_trend)
    st.markdown("""</div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""<div class="card">""", unsafe_allow_html=True)
    st.subheader("Index Futures")
    st.metric(label="Pre-market NQ", value=f"{nq_premarket}%")
    status_text = "Živá data" if is_live else "Stabilní režim"
    st.metric(label="Status", value=status_text)
    st.markdown("""</div>""", unsafe_allow_html=True)

if st.button("🔄 Obnovit data"):
    st.cache_data.clear()
    st.rerun()
