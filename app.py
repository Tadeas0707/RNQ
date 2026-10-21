from datetime import datetime
import zoneinfo
import feedparser
import google.generativeai as genai
from PIL import Image, ImageEnhance
import streamlit as st

# Nastavení aplikace
st.set_page_config(
    page_title="NQ Daytrading AI Agent - Funded Ultimate Safety",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ NQ Daytrading AI Agent (Funded Safety & Any-Session Mode)")
st.markdown(
    "Institucionální analytický systém optimalizovaný pro ochranu funded účtu."
    " Vyhledává bezpečné vstupy napříč celou seancí mimo nebezpečné otvírací"
    " zóny."
)

# Postranní panel
with st.sidebar:
  st.header("Konfigurace")
  api_key = st.text_input("Zadej Google Gemini API Key", type="password")
  if api_key:
    genai.configure(api_key=api_key)
  st.markdown("---")
  st.info(
      "💡 Systém vyhledává obchody v jakémkoliv poklidném časovém okně s"
      " důrazem na retest a ochranu před Stop Hunjem."
  )


# 1. Časový filtr pro kontrolu obchodních hodin a otvíracího okna
def check_trading_window():
  try:
    prague_tz = zoneinfo.ZoneInfo("Europe/Prague")
    now = datetime.now(prague_tz)
  except Exception:
    now = datetime.now()

  current_time_str = now.strftime("%H:%M")
  hour = now.hour
  minute = now.minute

  # Kontrola otvíracího okna (15:30 - 15:45 SEČ)
  is_opening_window = hour == 15 and 30 <= minute <= 45

  # Kontrola americké obědové pauzy (18:00 - 19:30 SEČ)
  is_lunch_break = (hour == 18) or (hour == 19 and minute < 30)

  return current_time_str, is_opening_window, is_lunch_break


# 2. Optimalizace obrázků (Pillow - kontrast a ostrost)
def process_image(image_file):
  img = Image.open(image_file).convert("RGB")
  enhancer = ImageEnhance.Contrast(img)
  img = enhancer.enhance(1.2)
  sharpness = ImageEnhance.Sharpness(img)
  img = sharpness.enhance(1.3)
  return img


# 3. Inteligentní filtr makro zpráv & DXY / US10Y / VIX & Red-Flag skener
def fetch_filtered_news():
  rss_url = "https://news.google.com/rss/search?q=(Nasdaq+OR+NQ+OR+Fed+OR+FOMC+OR+CPI+OR+USD+OR+DXY+OR+treasury+yields+OR+VIX)+when:1d&hl=en-US&gl=US&ceid=US:en"
  feed = feedparser.parse(rss_url)

  relevant_keywords = [
      "fomc",
      "cpi",
      "fed",
      "rates",
      "inflation",
      "nfp",
      "payrolls",
      "nasdaq",
      "futures",
      "powell",
      "vix",
      "dxy",
      "dollar",
      "yields",
      "treasury",
  ]
  headlines = []
  red_flags = []

  for entry in feed.entries[:15]:
    title_lower = entry.title.lower()
    if any(kw in title_lower for kw in relevant_keywords):
      headlines.append(f"- {entry.title} ({entry.published})")

      if any(
          rf in title_lower
          for rf in [
              "cpi",
              "fomc rate decision",
              "non-farm payrolls",
              "powell speaks",
          ]
      ):
        red_flags.append(entry.title)

  news_text = (
      "\n".join(headlines[:10])
      if headlines
      else "Žádné zásadní makro zprávy za 24h nebyly nalezeny."
  )
  has_red_flag = len(red_flags) > 0

  return news_text, has_red_flag, red_flags


# Kontrola času při načtení
curr_time, is_open_win, is_lunch = check_trading_window()

# Rozvržení - Vstupy
col1, col2 = st.columns(2)

with col1:
  st.subheader("1. Živé makro zprávy (DXY, US10Y, VIX) & Red-Flag")
  st.caption(f"🕒 Aktuální čas (SEČ): **{curr_time}**")

  if is_open_win:
    st.warning(
        "⚠️ **Upozornění:** Právě probíhá divoké otvírací okno (15:30 - 15:45"
        " SEČ). Vysoké riziko falešných průrazů a lovu Stop Lossů!"
    )

  if is_lunch:
    st.warning(
        "⚠️ **Upozornění:** Právě probíhá americká obědová pauza (18:00 - 19:30"
        " SEČ). Nízká likvidita."
    )

  if st.button("🔄 Načíst a přefiltrovat zprávy (vč. DXY, Výnosů & VIX)"):
    with st.spinner("Skenuji mezitržní korelátory a makro..."):
      news, red_flag, rf_list = fetch_filtered_news()
      st.session_state["news"] = news
      st.session_state["red_flag"] = red_flag
      st.session_state["rf_list"] = rf_list

  if "news" in st.session_state:
    if st.session_state.get("red_flag"):
      st.error(
          "🚨 **POZOR: Detekována HIGH-IMPACT Red-Flag událost!**\n"
          + "\n".join(st.session_state["rf_list"])
      )
    st.text_area(
        "Filtrované makro, DXY, Výnosy a VIX pro AI:",
        st.session_state["news"],
        height=180,
        disabled=True,
    )
  else:
    st.info("Klikni na tlačítko pro načtení makro dat.")

with col2:
  st.subheader("2. Multi-Timeframe Grafy (Any-Session Safety Mode)")
  st.caption(
      "AI vyhledá příležitost v jakékoliv fázi dne (mimo nebezpečný Open) s"
      " důrazem na retest a ochranu účtu."
  )

  tf_higher = st.selectbox(
      "Časový rámec 1. grafu (Vyšší TF):", ["15M", "1H", "4H"], index=0
  )
  img1_file = st.file_uploader(
      f"1. Vyšší TF ({tf_higher}) - Trend & S/R zóny",
      type=["png", "jpg", "jpeg"],
  )

  tf_lower = st.selectbox(
      "Časový rámec 2. grafu (Nižší TF - Vstupní):", ["1M", "3M", "5M"], index=2
  )
  img2_file = st.file_uploader(
      f"2. Nižší TF ({tf_lower}) - Detail vstupu / Price Action",
      type=["png", "jpg", "jpeg"],
  )

st.markdown("---")

# Zabalení odeslání do formuláře
with st.form("analysis_form"):
  st.subheader("3. Spuštění Funded Analýzy")
  submit_button = st.form_submit_button(
      "🚀 Vyhodnotit Multi-Timeframe Scénář", type="primary"
  )

if submit_button:
  if not api_key:
    st.error("Chybí Google Gemini API klíč v postranním panelu!")
  elif "news" not in st.session_state or img1_file is None:
    st.warning(
        "Nahráním alespoň 1. grafu (Vyšší TF) a načtením zpráv aktivuješ"
        " analýzu!"
    )
  else:
    with st.spinner("AI provádí analýzu v režimu ochrany Funded účtu..."):
      try:
        model = genai.GenerativeModel("gemini-3.8-flash")

        images_payload = []
        img1 = process_image(img1_file)
        images_payload.append(img1)

        img2_status = "Nenahrán (použit jednografový režim)"
        if img2_file is not None:
          img2 = process_image(img2_file)
          images_payload.append(img2)
          img2_status = f"Nahrán ({tf_lower})"

        prompt = f"""
Jsi nekompromisní šéf-risk manager pro Funded Tradery (Apex/Topstep). Klient má posledních pár pokusů a tvým jediným úkolem je OCHRANA KAPITÁLU, ale zároveň schopnost Najít čistý obchod V JAKÉMKOLIV ČASOVÉM OKNĚ DNE, pokud je trh po otvíracím výplachu a v klidné strukturální fázi.

PŘÍSNÁ BEZPEČNOSTNÍ PRAVIDLA PRO VYHODNOCENÍ:
1. **Filtrování nebezpečných oken (Opening & Red-Flags):** 
   - Pokud je čas mezi 15:30 a 15:45 SEČ (otvírací manipulace) nebo probíhá aktivní vyhlášení Red-Flag zprávy, povinně vydej **NO TRADE**.
   - Mimo toto okno (např. 16:00, 17:00, 20:00 SEČ) aktivně vyhledávej čisté příležitosti v jakékoliv fázi seance.
2. **Pravidlo Retestu (Anti-Sweep):** Nikdy nevolej vstup na první dotek S/R zóny. Vstup plánuj až PO proběhlém vybrání likvidity (Liquidity Sweep) a následném potvrzeném retestu (zavření svíčky s knotem/engulfing).
3. **Bezpečnostní polštář pro Stop Loss:** Stop Loss umísti s polštářem dál za očividné knoty svíček, aby ho instituce nemohly snadno vyhmátnout.
4. **Minimální skóre konfluence 85 bodů:** Pokud je trh nečitelný, vydat **NO TRADE**. Pokud je struktura jasná a retest potvrdil směr, schval obchod.

VÝSTUPNÍ STRUKTURA (Odpověz striktně v češtině):

1. **Bezpečnostní audit časového okna:** [Zhodnocení, zda aktuální čas a makro poskytují bezpečné prostředí pro obchod]
2. **Analýza struktury a retestu:** [Kde proběhl Liquidity Sweep a jak vypadá potvrzený retest]
3. **Matematické skóre konfluence:** [X / 100 bodů]
4. **Finální Verdikt / Směr:** [LONG / SHORT / NO TRADE]
5. **Přesná Vstupní Zóna (Až po retestu):** [Cenová hladina]
6. **Take Profit (TP):** [Cílová cena]
7. **Stop Loss (S bezpečnostním polštářem):** [Hladina ukrytá pod/nad likviditou]
8. **Kalkulace RRR:** [Minimálně 1:2]
9. **FUNDED TRADING SHRNUTÍ:** [Tučně: VERDIKT + Vstup | SL | TP]
"""

        response = model.generate_content([prompt] + images_payload)

        st.success("Analýza byla úspěšně vygenerována!")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"Nastala chyba při komunikaci s API: {e}")
