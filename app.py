from datetime import datetime
import zoneinfo
import feedparser
import google.generativeai as genai
from PIL import Image, ImageEnhance
import streamlit as st

# Nastavení aplikace
st.set_page_config(
    page_title="NQ quantitative terminal - Institutional Edition",
    page_icon="⚡",
    layout="wide",
)

st.title(
    "⚡ NQ Daytrading AI Agent (Time-Gated, VIX-Aware & RRR Math System)"
)
st.markdown(
    "Institucionální analytický systém pro daytrading Nasdaq (NQ) futures."
    " Kombinuje Multi-Timeframe Price Action, detekci VIXu, časový filtr a"
    " kalkulaci RRR."
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


# 3. Inteligentní filtr makro zpráv & VIX & Red-Flag skener
def fetch_filtered_news():
  # Hledáme cílená makro data včetně VIXu a úrokových sazeb
  rss_url = "https://news.google.com/rss/search?q=(Nasdaq+OR+NQ+OR+Fed+OR+FOMC+OR+CPI+OR+USD+OR+VIX)+when:1d&hl=en-US&gl=US&ceid=US:en"
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
      "volatility",
  ]
  headlines = []
  red_flags = []

  for entry in feed.entries[:15]:
    title_lower = entry.title.lower()
    if any(kw in title_lower for kw in relevant_keywords):
      headlines.append(f"- {entry.title} ({entry.published})")

      # Detekce Red-Flag událostí
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
      "\n".join(headlines[:8])
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
  st.subheader("1. Živé makro zprávy & Red-Flag Skener")
  st.caption(f"🕒 Aktuální čas (SEČ): **{curr_time}**")

  if is_lunch:
    st.warning(
        "⚠️ **Upozornění:** Právě probíhá americká obědová pauza (18:00 - 19:30"
        " SEČ). Trh má nízkou likviditu a zvýšené riziko falešných pohybů."
    )

  if st.button("🔄 Načíst a přefiltrovat zprávy (vč. VIX)"):
    with st.spinner("Skenuji makro události a VIX..."):
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
        "Filtrované zprávy a VIX pro AI:",
        st.session_state["news"],
        height=180,
        disabled=True,
    )
  else:
    st.info("Klikni na tlačítko pro načtení makro dat.")

with col2:
  st.subheader("2. Multi-Timeframe Grafy (TradingView)")
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

# Tlačítko pro spuštění vyhodnocení
if st.button("🚀 Vyhodnotit Multi-Timeframe Scénář", type="primary"):
  if not api_key:
    st.error("Chybí Google Gemini API klíč v postranním panelu!")
  elif "news" not in st.session_state or img1_file is None:
    st.warning(
        "Nahráním alespoň 1. grafu (Vyšší TF) a načtením zpráv aktivuješ"
        " analýzu!"
    )
  else:
    with st.spinner(
        "AI provádí hloubkovou Chain-of-Thought analýzu a výpočet RRR..."
    ):
      try:
        model = genai.GenerativeModel("gemini-3.8-flash")

        # Zpracování nahrávaných obrázků
        images_payload = []
        img1 = process_image(img1_file)
        images_payload.append(img1)

        img2_status = "Nenahrán (použit jednografový režim)"
        if img2_file is not None:
          img2 = process_image(img2_file)
          images_payload.append(img2)
          img2_status = f"Nahrán ({tf_lower})"

        # Pokročilý prompt s VIXem, Time-Gatingem a Matematikou RRR
        prompt = f"""
Jsi špičkový institucionální kvantitativní trader a risk manager zaměřený na daytrading Nasdaq (NQ) futures.
Tvým úkolem je provést nekompromisně přesnou Multi-Timeframe analýzu s důrazem na matematiku RRR a časové okno.

DODANÉ VSTUPY:
- **Aktuální čas analýzy (SEČ):** {curr_time}
- **Status obědové pauzy:** {'ANO (Zvýšené riziko)' if is_lunch else 'NE (Standardní hodiny)'}
- **Vyšší časový rámec (TF1):** {tf_higher}
- **Nižší časový rámec (TF2):** {img2_status}
- **Makro zprávy & VIX:** {st.session_state.get('news')}
- **Red-Flag Varování:** {st.session_state.get('red_flag')}

PROVEDEŠ ANALÝZU KROK ZA KROKEM (CHAIN-OF-THOUGHT):

**KROK 1: Makro Kontext, VIX & Časové Okno**
- Vyhodnoť náladu trhu z VIXu a makra. Zhodnoť, zda aktuální čas ({curr_time}) spadá do obědové pauzy nebo před Red-Flag událost.

**KROK 2: Analýza Vyššího TF ({tf_higher}) & Nižšího TF**
- Urči trend, S/R zóny, Order Blocky a zkontroluj případné fakeouty (falešná proražení pre-market high/low pro vymetení retailu).

**KROK 3: Výpočet Matematického RRR (Risk-Reward Ratio)**
- Definuj přesný Vstup, TP a SL. Počítej RRR = (TP - Vstup) / (Vstup - SL).
- **STRIKTNÍ PRAVIDLO:** Pokud je vyčíslené RRR MENŠÍ NEŽ 1:2 (tj. < 2.0), trade zamítni s verdiktem **NO TRADE**.

**KROK 4: Výpočet Matematického Skóre Konfluence (0-100 bodů)**
- Makro + VIX prostředí: 0 až 30 bodů
- Jasná S/R úroveň na vyšším TF: 0 až 30 bodů
- Čistá struktura na nižším TF (bez pasti) + RRR >= 1:2: 0 až 40 bodů
*CELKOVÉ SKÓRE KONFLUENCE:* (sečti body)

**PROVOZNÍ PRAVIDLO:** Pokud je celkové skóre NIŽŠÍ NEŽ 80 BODŮ, tvůj finální verdikt MUSÍ BÝT **"NO TRADE"**.

VÝSTUPNÍ STRUKTURA (Odpověz striktně v češtině v tomto formátu):

1. **Časový & VIX Manažment:** [Zhodnocení času {curr_time}, stavu VIXu a doporučené pauzy po zprávách]
2. **Detailní myšlenkový postup (Chain-of-Thought):** (Stručný popis analýzy)
3. **Matematické skóre konfluence:** [X / 100 bodů]
4. **Finální Verdikt / Směr:** [LONG / SHORT / NEUTRAL / NO TRADE]
5. **Přesná Vstupní Zóna:** [Cenová hladina]
6. **Take Profit (TP) + Odhad času:** [Cílová cena + předpokládaný čas v minutách do dosažení TP]
7. **Podmíněný Stop Loss / Invalidace:** [Přesná hladina + podmínka uzavření svíčky]
8. **Kalkulace RRR:** [Přesný vypočtený poměr RRR, např. 1:2.4]
9. **Doporučení pro řízení rizika:** (Doporučený postup pro posun na Breakeven)
"""

        # Odeslání požadavku na Gemini
        response = model.generate_content([prompt] + images_payload)

        st.success("Analýza byla úspěšně vygenerována!")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"Nastala chyba při komunikaci s API: {e}")
