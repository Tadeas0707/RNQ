from datetime import datetime
import zoneinfo
import feedparser
import google.generativeai as genai
from PIL import Image, ImageEnhance
import streamlit as st

# Nastavení aplikace
st.set_page_config(
    page_title="NQ Daytrading AI Agent - Fully Automated Quant Edition",
    page_icon="⚡",
    layout="wide",
)

st.title(
    "⚡ NQ Daytrading AI Agent (Fully Automated Vision & Quant System)"
)
st.markdown(
    "Institucionální analytický systém pro daytrading Nasdaq (NQ) futures."
    " AI sama odvodí kontext seance, gapy i trend z nahraných grafů."
)

# Postranní panel
with st.sidebar:
  st.header("Konfigurace")
  api_key = st.text_input("Zadej Google Gemini API Key", type="password")
  if api_key:
    genai.configure(api_key=api_key)
  st.markdown("---")
  st.info(
      "💡 Pro maximální úspěšnost prováděj analýzu v 15:30 SEČ nebo při"
      " testu klíčové S/R zóny."
  )


# 1. Časový filtr (Time-Gating) pro kontrolu obchodních hodin
def check_trading_window():
  try:
    prague_tz = zoneinfo.ZoneInfo("Europe/Prague")
    now = datetime.now(prague_tz)
  except Exception:
    now = datetime.now()

  current_time_str = now.strftime("%H:%M")
  hour = now.hour
  minute = now.minute

  # Kontrola americké obědové pauzy (18:00 - 19:30 SEČ)
  is_lunch_break = (hour == 18) or (hour == 19 and minute < 30)

  # Kontrola hlavního okna (15:30 - 22:00 SEČ)
  is_main_session = (hour == 15 and minute >= 30) or (16 <= hour < 22)

  return current_time_str, is_lunch_break, is_main_session


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
curr_time, is_lunch, is_main = check_trading_window()

# Rozvržení - Vstupy
col1, col2 = st.columns(2)

with col1:
  st.subheader("1. Živé makro zprávy (DXY, US10Y, VIX) & Red-Flag")
  st.caption(f"🕒 Aktuální čas (SEČ): **{curr_time}**")

  if is_lunch:
    st.warning(
        "⚠️ **Upozornění:** Právě probíhá americká obědová pauza (18:00 - 19:30"
        " SEČ). Trh má nízkou likviditu a zvýšené riziko falešných pohybů."
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
  st.subheader("2. Multi-Timeframe Grafy (Auto-Analysis)")
  st.caption(
      "AI automaticky detekuje trend, gapy i strukturu přímo z nahraných"
      " screenshotů."
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

# Zabalení odeslání do formuláře k prevenci duplicitních požadavků (ochrana před 429 RPM)
with st.form("analysis_form"):
  st.subheader("3. Spuštění analýzy")
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
    with st.spinner(
        "AI vizuálně analyzuje grafy, provádí Chain-of-Thought a výpočet RRR..."
    ):
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
Jsi elitní kvantitativní trader a institucionální risk manager zaměřený výhradně na daytrading Nasdaq (NQ) futures.
Tvým úkolem je provést nemilosrdně přísnou Multi-Timeframe analýzu s využitím mezitržních korelací (DXY/Yields), konceptu MSS (Market Structure Shift) a dvoufázové oponentury.

DODANÉ VSTUPY:
- **Aktuální čas analýzy (SEČ):** {curr_time}
- **Status obědové pauzy:** {'ANO (Zvýšené riziko)' if is_lunch else 'NE (Standardní hodiny)'}
- **Kontext seance (ODVOĎ AUTOMATICKY Z GRAFU):** Vizuálně zkontroluj nahraný graf (zda trh otevřel s gapem, zda je přítomen silný včerejší trend, nebo probíhá konsolidace).
- **Vyšší časový rámec (TF1):** {tf_higher}
- **Nižší časový rámec (TF2):** {img2_status}
- **Makro zprávy (DXY, Yields, VIX, Fed):** {st.session_state.get('news')}
- **Red-Flag Varování:** {st.session_state.get('red_flag')}

PROVEDEŠ ANALÝZU KROK ZA KROKEM (CHAIN-OF-THOUGHT & SELF-REFLECTION):

**KROK 1: Mezitržní analýza (DXY & US10Y) a VIX**
- Zhodnoť, zda vývoj na US Dolaru (DXY) nebo výnosech 10letých dluhopisů (US10Y) nepotvrzuje falešné proražení na NQ. Pokud DXY/Yields posilují, buď extrémně opatrný u Longů na NQ.

**KROK 2: Vizuální analýza Vyššího TF ({tf_higher}) & Kontext Seance**
- Automaticky detekuj kontext z grafu (gap open, včerejší trend, akumulace/distribuce) a urči klíčové S/R úrovně.

**KROK 3: Kontrola Market Structure Shift (MSS) na Nižším TF**
- NEVOLEJ VSTUP při prvním nepotvrzeném doteku S/R zóny!
- Vyžaduj potvrditelnou změnu struktury (MSS / BOS / zamítnutí zóny knotem svíčky / engulfing pattern). Pokud změna struktury chybí, vyhodnoť jako **"NO TRADE"**.

**KROK 4: Interní Oponentura (Self-Reflection / Devil's Advocate)**
- Než dáš finální verdikt, povinně se v roli Risk Managera pokus tento obchod zpochybnit. Vypiš hlavní 2 rizika, proč by tento obchod mohl selhat.

**KROK 5: Výpočet RRR a Skóre Konfluence (0-100 bodů)**
- Vypočítej RRR = (TP - Vstup) / (Vstup - SL). Pokud je RRR < 1:2 (tj. < 2.0), obchodu vystav stopku (**NO TRADE**).
- Přiděl body: Makro+DXY+VIX (0-30b), Vyšší TF S/R zóna (0-30b), MSS struktura + RRR >= 1:2 na nižším TF (0-40b).
*CELKOVÉ SKÓRE KONFLUENCE:* (sečti body)

**PROVOZNÍ PRAVIDLO:** Pokud je celkové skóre NIŽŠÍ NEŽ 80 BODŮ, nebo pokud probíhá aktivní Red-Flag či chybí MSS, tvůj finální verdikt MUSÍ BÝT **"NO TRADE"**.

VÝSTUPNÍ STRUKTURA (Odpověz striktně v češtině v tomto formátu):

1. **Mezitržní & Časové Zhodnocení (DXY / Yields / VIX / Čas):** [Stručné hodnocení korelací a času]
2. **Detailní myšlenkový postup (Chain-of-Thought & MSS):** [Popis vyššího TF, vizuálně detekovaného kontextu a struktury MSS]
3. **Interní Oponentura (Rizika obchodu):** [2 hlavní důvody, proč by trade mohl selhat]
4. **Matematické skóre konfluence:** [X / 100 bodů]
5. **Finální Verdikt / Směr:** [LONG / SHORT / NEUTRAL / NO TRADE]
6. **Přesná Vstupní Zóna:** [Cenová hladina s potvrzením MSS]
7. **Take Profit (TP) + Odhad času:** [Cílová cena + předpokládaný časový horizont do dosažení TP]
8. **Podmíněný Stop Loss / Invalidace:** [Přesná hladina + podmínka uzavření svíčky]
9. **Kalkulace RRR:** [Přesný vypočtený poměr RRR, např. 1:2.5]
10. **Doporučení pro exekuci & Posun na BE:** (Stručné rady)
"""

        response = model.generate_content([prompt] + images_payload)

        st.success("Analýza byla úspěšně vygenerována!")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"Nastala chyba při komunikaci s API: {e}")
