import streamlit as st

# --- BEZPEČNÝ IMPORT YFINANCE ---
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="MNQ Opening Bias Scouter (Live)",
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
st.caption("Window: 15:30 - 17:00 SEČ | Živá data / Fallback režim")

# --- STAHOVÁNÍ DAT ---
@st.cache_data(ttl=300)
def fetch_live_data():
    if not YFINANCE_AVAILABLE:
        return {"success": False, "error": "Knihovna yfinance není nainstalována."}
    try:
        vix = yf.Ticker("^VIX").history(period="2d")
        tnx = yf.Ticker("^TNX").history(period="2d")
        nq = yf.Ticker("NQ=F").history(period="2d")

        vix_val = round(vix['Close'].iloc[-1], 2)
        vix_change = round(vix_val - vix['Close'].iloc[-2], 2)

        tnx_val = tnx['Close'].iloc[-1]
        tnx_prev = tnx['Close'].iloc[-2]
        us10y_trend = "DOWN" if tnx_val < tnx_prev else "UP"

        nq_close = nq['Close'].iloc[-1]
        nq_open = nq['Open'].iloc[-1]
        nq_pct = round(((nq_close - nq_open) / nq_open) * 100, 2)

        return {
            "success": True,
            "vix": vix_val,
            "vix_change": vix_change,
            "us10y_trend": us10y_trend,
            "nq_premarket": nq_pct
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

market = fetch_live_data()

if not market["success"]:
    st.warning(f"⚠️ Živá data nedostupná (důvod: {market.get('error', 'Neznámá chyba')}). Běžím v záložním režimu.")
    vix_val, vix_change, us10y_trend, nq_premarket = 16.4, -0.4, "DOWN", 0.52
else:
    vix_val = market["vix"]
    vix_change = market["vix_change"]
    us10y_trend = market["us10y_trend"]
    nq_premarket = market["nq_premarket"]

# --- VY
