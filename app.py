<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MNQ Wall Street Opening Scouter</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --border-color: #30363d;
            --text-color: #c9d1d9;
            --green: #238636;
            --red: #da3633;
            --yellow: #d29922;
            --blue: #58a6ff;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }

        .container {
            max-width: 900px;
            width: 100%;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }

        h1 { font-size: 1.4rem; margin: 0; color: #fff; }
        .badge { background: var(--border-color); padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; }

        .bias-card {
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 25px;
            text-align: center;
            margin-bottom: 25px;
        }

        .bias-title { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; }
        .bias-value { font-size: 2.2rem; font-weight: bold; margin: 10px 0; }
        .bias-desc { font-size: 0.95rem; line-height: 1.4; color: #8b949e; }

        .bullish { color: #3fb950; border-color: var(--green); }
        .bearish { color: #f85149; border-color: var(--red); }
        .neutral { color: var(--yellow); border-color: var(--yellow); }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 15px;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
        }

        .card h3 {
            margin-top: 0;
            font-size: 1rem;
            color: #fff;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            font-size: 0.9rem;
        }

        .metric-val { font-weight: bold; }

        button {
            background: var(--blue);
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
        }

        button:hover { opacity: 0.9; }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>MNQ Opening Bias Scouter</h1>
        <span class="badge">Window: 15:30 - 17:00 SEČ</span>
    </header>

    <div class="bias-card" id="mainBiasCard">
        <div class="bias-title">Wall Street Opening Bias</div>
        <div class="bias-value" id="biasStatus">ANALYZUJÍ SE DATA...</div>
        <div class="bias-desc" id="biasReason">Načítání nejnovějších dat z makro kalendáře, výnosů US10Y a indexu VIX.</div>
    </div>

    <div class="grid">
        <!-- Makro Kalendář -->
        <div class="card">
            <h3>Makroekonomická Data</h3>
            <div class="metric"><span>CPI / PCE Inflace:</span> <span class="metric-val" id="cpiStatus">-</span></div>
            <div class="metric"><span>NFP / Zaměstnanost:</span> <span class="metric-val" id="nfpStatus">-</span></div>
            <div class="metric"><span>Fed / Rozhodnutí:</span> <span class="metric-val" id="fedStatus">-</span></div>
        </div>

        <!-- Volatilita a Trh -->
        <div class="card">
            <h3>Tržní Podmínky</h3>
            <div class="metric"><span>VIX Index:</span> <span class="metric-val" id="vixVal">-</span></div>
            <div class="metric"><span>US 10Y Yields:</span> <span class="metric-val" id="us10yVal">-</span></div>
            <div class="metric"><span>Pre-Market NQ:</span> <span class="metric-val" id="nqPremarket">-</span></div>
        </div>

        <!-- Dominantní Earnings -->
        <div class="card">
            <h3>Magnificent 7 Earnings</h3>
            <div class="metric"><span>Dnešní Výsledky:</span> <span class="metric-val" id="earningsStatus">-</span></div>
            <div class="metric"><span>Impakt na Nasdaq:</span> <span class="metric-val" id="earningsImpact">-</span></div>
        </div>
    </div>

    <button onclick="runScout()">Znova Skenovat Trh</button>
</div>

<script src="scouter.js"></script>
</body>
</html>
