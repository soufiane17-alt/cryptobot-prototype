from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from bot.exchange import get_price
from bot.signals import get_signal
import time

app = FastAPI(title="CryptoBot Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CryptoBot — Prototype</title>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    :root { --bg: #0d0d0d; --card: #141414; --border: rgba(255,255,255,0.1); --green: #22c55e; --red: #ef4444; }
    body { background: var(--bg); color: #f0f0f0; font-family: 'IBM Plex Sans', sans-serif; margin:0; padding:0; }
    .header { background: #111; padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }
    .logo { font-family: 'IBM Plex Mono', monospace; font-size: 22px; font-weight: 600; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin: 20px 0; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px 10px; text-align: left; border-bottom: 1px solid var(--border); }
    .buy { color: var(--green); font-weight: 600; }
    .sell { color: var(--red); font-weight: 600; }
  </style>
</head>
<body>
<div class="header">
  <div class="logo">CryptoBot Prototype</div>
  <div>LIVE • EN TEMPS RÉEL</div>
</div>

<div style="max-width:1200px; margin:0 auto; padding:20px;">
  <div class="card">
    <h2>Prix en temps réel</h2>
    <div id="prices" style="font-family:monospace; font-size:1.4rem;"></div>
  </div>

  <div class="card">
    <h2>Derniers signaux</h2>
    <table>
      <thead><tr><th>Heure</th><th>Paire</th><th>Signal</th><th>RSI</th><th>Score</th><th>Raison</th></tr></thead>
      <tbody id="signals"></tbody>
    </table>
  </div>
</div>

<script>
  async function update() {
    const res = await fetch('/api/status');
    const data = await res.json();

    document.getElementById('prices').innerHTML = `
      BTC/USDT : $${Number(data.btc_price).toLocaleString('fr-FR')}<br>
      ETH/USDT : $${Number(data.eth_price).toLocaleString('fr-FR')}<br>
      SOL/USDT : $${Number(data.sol_price).toLocaleString('fr-FR')}
    `;

    let html = '';
    data.recent_signals.forEach(s => {
      html += `<tr>
        <td>${new Date(s.timestamp*1000).toLocaleTimeString('fr-FR')}</td>
        <td>${s.symbol}</td>
        <td class="${s.signal.toLowerCase()}">${s.signal}</td>
        <td>${s.rsi}</td>
        <td>${s.score}/100</td>
        <td>${s.reason}</td>
      </tr>`;
    });
    document.getElementById('signals').innerHTML = html || '<tr><td colspan="6" style="text-align:center;color:#666;">Aucun signal pour le moment</td></tr>';
  }

  setInterval(update, 4000);
  update();
</script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(HTML_DASHBOARD)

@app.get("/api/status")
async def status():
    return {
        "btc_price": get_price("BTC/USDT"),
        "eth_price": get_price("ETH/USDT"),
        "sol_price": get_price("SOL/USDT"),
        "recent_signals": [{**get_signal(sym), "symbol": sym} for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]]
    }
