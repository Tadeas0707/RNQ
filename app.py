import feedparser
import google.generativeai as genai
from PIL import Image
import streamlit as st

# Nastavení stránky
st.set_page_config(
    page_title="NQ Daytrading AI Agent", page_icon="⚡", layout="wide"
)

st.title("⚡ NQ Daytrading AI Agent (Intradenní Trend & Predikce)")
st.markdown(
    "Aplikace zaměřená na **daytrading Nasdaq futures (NQ)**. Kombinuje"
    " automatické makro zprávy a Price Action pro určení intradenního trendu,"
    " cílové ceny a procentuální šance."
)

# Postranní panel pro API klíč
st.sidebar.header("Konfigurace")
api_key = st.sidebar.text_input(
    "Zadej Google Gemini API Key",
    type="password",
    help="Získej zdarma na aistudio.google.com",
)

if api_key:
  genai.configure(api_key=api_key)
else:
  st.sidebar.warning("Prosím zadej svůj bezplatný API klíč.")


# Funkce pro stažení živých zpráv
@st.cache_data(ttl=300)
def fetch_latest_news():
  rss_url = "https://news.google.com/rss/search?q=Nasdaq+NQ+futures+stock+market+macro&hl=en-US&gl=US&ceid=US:en"
  feed = feedparser.parse(rss_url)
  headlines = []
  for entry in feed.entries[:10]:
    headlines.append(f"- {entry.title} ({entry.published})")
  return "\n".join(headlines)


# Rozvržení aplikace
col1, col2 = st.columns(2)

with col1:
  st.subheader("1. Živé makro zprávy (Auto-RSS)")
  if st.button("🔄 Načíst čerstvé zprávy z trhu"):
    with st.spinner("Stahuji zprávy..."):
      st.session_state["news"] = fetch_latest_news()

  if "news" in st.session_state:
    st.text_area(
        "Zprávy pro AI:", st.session_state["news"], height=200, disabled=True
    )
  else:
    st.info("Klikni na tlačítko pro stažení zpráv.")

with col2:
  st.subheader("2. TradingView Screenshot (Intradenní graf)")
  uploaded_file = st.file_uploader(
      "Nahraj graf NQ (např. M1, M5, M15)", type=["png", "jpg", "jpeg"]
  )
  if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(
        image, caption="Detail intradenního grafu", use_container_width=True
    )

# Spuštění analýzy
st.markdown("---")
if st.button("🚀 Vyhodnotit Daytrade Scénář", type="primary"):
  if not api_key:
    st.error("Chybí Gemini API klíč v postranním panelu!")
  elif "news" not in st.session_state or uploaded_file is None:
    st.warning("Ujisti se, že máš načtené zprávy i nahraný graf!")
  else:
    with st.spinner("AI vyhodnocuje intradenní Price Action a makro..."):
      try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Prompt zaměřený na daytrading, trend, přesnou cenu a procentuální šanci
        prompt = f"""
                Jsi elitní intradenní daytrader na Nasdaq 100 futures (NQ). Zaměřuješ se výhradně na DAYTRADING a skalpování (horizont v řádu minut až hodin, maximálně do konce dnešní seance).

                ANALYZUJ NÁSLEDUJÍCÍ DATA:
                1. Přiložený detailní screenshot grafu (hledej S/R zóny, liquidity sweeps, momentum, svíčkové formace a intradenní strukturu).
                2. Aktuální zprávy z trhu:
                {st.session_state['news']}

                POSKYTNI ODPOVĚĎ V TOMTO ZPRACUJE PODROBNÉM FORMÁTU:

                ### 📌 INTRADENNÍ TREND
                - **Očekávaný trend**: [BULLISH / BEARISH / SIDEWAYS]
                - **Procentuální pravděpodobnost naplnění**: [X %] (např. 75 %)

                ### 🎯 CÍLOVÁ CENA NQ
                - **Předpokládaná cílová cena (Take Profit)**: [Přesná cenová hladina NQ, např. 20 450]
                - **Invalidace scénáře (Stop Loss zóna)**: [Cenová hladina, kde scénář přestává platit]

                ### 🔍 DETAILECH O PRICE ACTION & MAKRO
                - **Struktura trhu (Graf)**: Co přesně vidíš na grafu za daytrading příležitost.
                - **Vliv makro zpráv**: Jak stažené zprávy ovlivňují dnešní volatility a směr.
                - **Doporučený postup**: Kdy vstoupit, na co si dát pozor při dnešním obchodování.
                """

        response = model.generate_content([prompt, image])

        st.success("Analýza je hotová!")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"Nastala chyba: {e}")
