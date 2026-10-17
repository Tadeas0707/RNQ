import feedparser
import google.generativeai as genai
from PIL import Image, ImageEnhance
import streamlit as st

# Nastavení aplikace
st.set_page_config(
    page_title="NQ Daytrading AI Agent - Pro Edition",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ NQ Daytrading AI Agent (Multi-Timeframe & Konfluenční Pro System)")
st.markdown(
    "Institucionální analytický systém pro daytrading Nasdaq (NQ) futures."
    " Kombinuje Multi-Timeframe Price Action, detekci makro rizika a matici"
    " konfluence."
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


# 1. Optimalizace obrázků (Pillow - úprava kontrastu a ostrosti pro AI)
def process_image(image_file):
  img = Image.open(image_file).convert("RGB")
  # Zvýšení kontrastu pro lepší čitelnost svíček
  enhancer = ImageEnhance.Contrast(img)
  img = enhancer.enhance(1.2)
  # Zvýšení ostrosti pro text a osy
  sharpness = ImageEnhance.Sharpness(img)
  img = sharpness.enhance(1.3)
  return img


# 2. Inteligentní filtr makro zpráv & Red-Flag detekce
def fetch_filtered_news():
  # Hledáme cílená makro data
  rss_url = "https://news.google.com/rss/search?q=(Nasdaq+OR+NQ+OR+Fed+OR+FOMC+OR+CPI+OR+USD)+when:1d&hl=en-US&gl=US&ceid=US:en"
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
      "treasury",
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


# Rozvržení - Vstupy
col1, col2 = st.columns(2)

with col1:
  st.subheader("1. Živé makro zprávy & Red-Flag Skener")
  if st.button("🔄 Načíst a přefiltrovat zprávy"):
    with st.spinner("Skenuji makro události..."):
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
        "Filtrované zprávy pro AI:",
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
        "AI provádí hloubkovou Chain-of-Thought analýzu a počítá skóre"
        " konfluence..."
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

        # Pokročilý prompt s Chain-of-Thought a Bodovacím systémem
        prompt = f"""
Jsi špičkový institucionální kvantitativní trader a risk manager zaměřený na daytrading Nasdaq (NQ) futures.
Tvým úkolem je provést nekompromisně přesnou Multi-Timeframe analýzu.

DODANÉ VSTUPY:
- **Vyšší časový rámec (TF1):** {tf_higher}
- **Nižší časový rámec (TF2):** {img2_status}
- **Makro zprávy:** {st.session_state.get('news')}
- **Red-Flag Varování:** {st.session_state.get('red_flag')}

PROVEDEŠ ANALÝZU KROK ZA KROKEM (CHAIN-OF-THOUGHT):

**KROK 1: Makro Kontext & Red-Flag Kontrola**
Vyhodnoť, zda aktuální fundamety podporují Long/Short nebo zda je trh před extrémně rizikovou událostí.

**KROK 2: Analýza Vyššího TF ({tf_higher})**
Urči hlavní trend, klíčové S/R úrovně, Order Blocky a kde se nachází hlavicová likvidita.

**KROK 3: Analýza Nižšího TF a Detekce Falešných Proražení (Fakeouts)**
Hledej strukturu (BOS, CHoCH) a zkontroluj, zda nedošlo k falešnému proražení (sweepu) předchozího High/Low pro vymetení retailových Stop Lossů.

**KROK 4: Výpočet Matematického Skóre Konfluence (0-100 bodů)**
Přiřaď body podle této matice:
- Podpora makro prostředí: 0 až 30 bodů
- Jasná S/R úroveň / Order Block na vyšším TF: 0 až 30 bodů
- Čistá struktura a potvrzený vstup na nižším TF (bez pasti): 0 až 40 bodů
*CELKOVÉ SKÓRE KONFLUENCE:* (sečti body)

**PROVOZNÍ PRAVIDLO:** Pokud je celkové skóre NIŽŠÍ NEŽ 80 BODŮ, tvůj finální verdikt MUSÍ BÝT **"NO TRADE"**.

VÝSTUPNÍ STRUKTURA (Odpověz striktně v češtině v tomto formátu):

1. **Detailní myšlenkový postup (Chain-of-Thought):** (Stručný popis Kroků 1-3)
2. **Matematické skóre konfluence:** [X / 100 bodů]
3. **Finální Verdikt / Směr:** [LONG / SHORT / NEUTRAL / NO TRADE]
4. **Přesná Vstupní Zóna:** [Cenová hladina]
5. **Take Profit (TP):** [Cílová cena - RRR min 1:2]
6. **Podmíněný Stop Loss / Invalidace:** [Přesná hladina + podmínka, např. 'pokud M5 svíčka zavře pod touto cenou']
7. **Doporučení pro exekuci:** (Stručné rady pro řízení obchodu)
"""

        # Odeslání požadavku na Gemini
        response = model.generate_content([prompt] + images_payload)

        st.success("Analýza byla úspěšně vygenerována!")
        st.markdown(response.text)

      except Exception as e:
        st.error(f"Nastala chyba při komunikaci s API: {e}")
