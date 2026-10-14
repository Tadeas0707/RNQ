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


# Funkce pro stažení živých makro zpráv bez cachování (vždy čerstvé po kliknutí)
def fetch_latest_news():
  # Čistý a spolehlivý dotaz s filtrem na posledních 24 hodin (when:1d)
  rss_url = "https://news.google.com/rss/search?q=Nasdaq+futures+Federal+Reserve+macro+when:1d&hl=en-US&gl=US&ceid=US:en"
  feed = feedparser.parse(rss_url)
  headlines = []
  for entry in feed.entries[:10]:
    headlines.append(f"- {entry.title} ({entry.published})")

  if not headlines:
    return (
        "Žádné čerstvé zprávy za posledních 24 hodin nebyly nalezeny."
        " Obchodujeme primárně podle Price Action z grafu."
    )

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
            model = genai.GenerativeModel("gemini-3.8-flash")

            # Definice promptu uvnitř try bloku
            prompt = f"""
Jsi špičkový profesionální kvantitativní trader a analytik se zaměřením na daytrading Nasdaq (NQ) futures.
Tvým úkolem je analyzovat přiložený screenshot grafu (Price Action, S/R úrovně, struktura trhu) společně s těmito čerstvými makro zprávami:
{st.session_state.get('news', 'Žádné zprávy k dispozici.')}

PRAVIDLA PRO VYHODNOCENÍ (BUĎ VELMI KRITICKÝ A PŘÍSNÝ):
1. NEHLEDEJ OBCHODY ZA KAŽDOU CENU. Pokud graf a makro nemají jasnou shodu nebo je trh v silné konsolidaci/šumu, dej nízkou pravděpodobnost úspěchu (pod 50 %).
2. Vysokou pravděpodobnost (nad 75-80 %) uděluj POUZE tehdy, když graf jasně ukazuje:
   - Test klíčové S/R úrovně (Support/Resistance) nebo Order Blocku.
   - Jasný konfluentní faktor s makro zprávami (např. silný USD/makro tisk podpořící trend).
   - Čistou strukturu Price Action (např. BOS - Break of Structure, CHoCH).
3. Vždy jasně definuj:
   - **Hlavní trend / Směr** (Long / Short / Neutral)
   - **Vstupní zónu**
   - **Cílovou cenu (Take Profit)** s reálným RRR (Risk-Reward Ratio alespoň 1:1,3)
   - **Invalidaci (Stop Loss)**
   - **Procentuální šanci na úspěch** (Buď realistický, 90% dávej jen naprostým výjimkám, kdy se slévá silná technická a makro úroveň).

Odpověď strukturuj přehledně v češtině.
"""

            response = model.generate_content([prompt, image])

            st.success("Analýza je hotová!")
            st.markdown(response.text)

          except Exception as e:
            st.error(f"Nastala chyba: {e}")
