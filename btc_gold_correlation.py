# btc_gold_correlation.py
# BTC vs Gold (PAXGUSDT on Binance) — 4 regimes, Aug 2025 – May 2026
# Run: python btc_gold_correlation.py

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ── CONFIG ──────────────────────────────────────────────────────────────────
REGIMES = {
    "1. Pre-ATH Bull\n(Aug 6 – Oct 6, 2025)":      ("2025-08-06", "2025-10-06"),
    "2. Post-ATH Drawdown\n(Oct 7 – Feb 27)":  ("2025-10-07", "2026-02-27"),
    "3. War\n(Feb 28 – Apr 7)":                  ("2026-02-28", "2026-04-07"),
    "4. Post-Ceasefire\n(Apr 8 – May 22)":       ("2026-04-08", "2026-05-22"),
}
ROLLING_WINDOW = 20
OUTPUT_PNG = "btc_gold_correlation.png"

# ── 1. Fetch BTCUSDT from Binance ───────────────────────────────────────────
def fetch_btc():
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": "1d", "limit": 1000}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.date
    df["close"] = df["close"].astype(float)
    return df[["date", "close"]].rename(columns={"close": "btc"})

# ── 2. Fetch PAXGUSDT (tokenized gold) from Binance ─────────────────────────
def fetch_gold():
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "PAXGUSDT", "interval": "1d", "limit": 1000}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.date
    df["close"] = df["close"].astype(float)
    return df[["date", "close"]].rename(columns={"close": "gold"})

# ── 3. Merge ─────────────────────────────────────────────────────────────────
print("Fetching BTC from Binance...")
btc = fetch_btc()

print("Fetching PAXGUSDT (Gold/USD) from Binance...")
gold = fetch_gold()

df = pd.merge(btc, gold, on="date", how="inner")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

start_dt = pd.Timestamp("2025-08-01")
end_dt = pd.Timestamp("2026-05-22")
df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)].copy()
df = df.dropna(subset=["btc", "gold"])

print(f"Merged: {len(df)} overlapping trading days")
print(f"Window: {df['date'].iloc[0].strftime('%Y-%m-%d')} → {df['date'].iloc[-1].strftime('%Y-%m-%d')}")

ath_row = df[df["date"] == "2025-10-06"]
if not ath_row.empty:
    print(f"BTC ATH: October 6, 2025 — ${ath_row['btc'].values[0]:,.0f}")
print()

# ── 4. Returns & Rolling Correlation ────────────────────────────────────────
df["btc_ret"] = df["btc"].pct_change()
df["gold_ret"] = df["gold"].pct_change()
df["rolling_corr"] = df["btc_ret"].rolling(ROLLING_WINDOW).corr(df["gold_ret"])

# ── 5. Per-Regime Stats ──────────────────────────────────────────────────────
print(f"{'='*65}")
print(f"  BTC vs PAXG (Tokenized Gold) — Correlation by Regime (20-day rolling)")
print(f"{'='*65}\n")

results = []
for label, (start, end) in REGIMES.items():
    mask = (df["date"] >= start) & (df["date"] <= end)
    sub = df[mask].dropna(subset=["btc_ret", "gold_ret"])
    if len(sub) < 4:
        continue
    overall = sub["btc_ret"].corr(sub["gold_ret"])
    avg_roll = sub["rolling_corr"].mean()
    min_roll = sub["rolling_corr"].min()
    max_roll = sub["rolling_corr"].max()
    btc_chg = (sub["btc"].iloc[-1] / sub["btc"].iloc[0] - 1) * 100
    gold_chg = (sub["gold"].iloc[-1] / sub["gold"].iloc[0] - 1) * 100
    results.append({"regime": label, "n_days": len(sub),
        "corr": overall, "avg_roll": avg_roll,
        "min_roll": min_roll, "max_roll": max_roll,
        "btc_chg": btc_chg, "gold_chg": gold_chg,
    })
    print(f"  {label}")
    print(f"    Days:                {len(sub)}")
    print(f"    Overall correlation: {overall:+.3f}")
    print(f"    Avg 20d rolling:      {avg_roll:+.3f}  (min: {min_roll:+.3f}  max: {max_roll:+.3f})")
    print(f"    BTC change:           {btc_chg:+.2f}%")
    print(f"    PAXG change:          {gold_chg:+.2f}%")
    print()

# ── 6. Regime Colours ────────────────────────────────────────────────────────
REGIME_COLORS = {
    "1. Pre-ATH Bull\n(Aug 6 – Oct 6, 2025)":     "#2DC653",
    "2. Post-ATH Drawdown\n(Oct 7 – Feb 27)": "#E63946",
    "3. War\n(Feb 28 – Apr 7)":                 "#FF6B35",
    "4. Post-Ceasefire\n(Apr 8 – May 22)":      "#4C9AFF",
}

# ── 7. Plot ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(15, 10), gridspec_kw={"height_ratios": [2.5, 2.5, 1.2]})
ax1, ax2, ax3 = axes

# Panel 1: indexed prices
btc_start = df["btc"].iloc[0]
gold_start = df["gold"].iloc[0]
df["btc_idx"] = df["btc"] / btc_start * 100
df["gold_idx"] = df["gold"] / gold_start * 100

for label, (start, end) in REGIMES.items():
    mask = (df["date"] >= start) & (df["date"] <= end)
    sub = df[mask]
    c = REGIME_COLORS[label]
    ax1.plot(sub["date"], sub["btc_idx"], color=c, linewidth=1.8,
             label=f"BTC  — {label.replace(chr(10), ' ')}")
    ax1.plot(sub["date"], sub["gold_idx"], color="gray", linewidth=1.2,
             linestyle="--", alpha=0.75)

# ATH annotation
ath_date = pd.Timestamp("2025-10-06")
ath_btc_idx = df.loc[df["date"] == ath_date, "btc_idx"].values
if len(ath_btc_idx) > 0:
    ax1.axvline(ath_date, color="gold", linewidth=1.5, linestyle="-.", alpha=0.8)
    ax1.annotate("BTC ATH\nOct 6\n$124,659",
                 xy=(ath_date, ath_btc_idx[0]),
                 xytext=(10, -30), textcoords="offset points",
                 fontsize=7.5, color="gold",
                 arrowprops=dict(arrowstyle="->", color="gold", alpha=0.7))

ax1.set_ylabel("Indexed to Aug 1, 2025 = 100", fontsize=10)
ax1.set_title("BTC vs PAXG (Tokenized Gold) — Pre-ATH Bull → War & Ceasefire "
              "(Aug 2025 – May 2026)", fontsize=13, fontweight="bold")
ax1.legend(loc="upper left", fontsize=7.5, ncol=2)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

for label in REGIMES:
    start = pd.Timestamp(REGIMES[label][0])
    if start > df["date"].iloc[0]:
        ax1.axvline(start, color="gray", linewidth=0.8, linestyle=":")

# Panel 2: rolling correlation
for label, (start, end) in REGIMES.items():
    mask = (df["date"] >= start) & (df["date"] <= end)
    sub = df[mask]
    c = REGIME_COLORS[label]
    ax2.plot(sub["date"], sub["rolling_corr"], color=c, linewidth=1.8,
             label=label.replace("\n", " "))
    ax2.fill_between(sub["date"], sub["rolling_corr"], 0, alpha=0.12, color=c)

ax2.axhline(0, color="black", linewidth=1)
ax2.axhline(0.5, color="green", linewidth=0.7, linestyle="--", alpha=0.5)
ax2.axhline(-0.5, color="red", linewidth=0.7, linestyle="--", alpha=0.5)
ax2.set_ylabel("20-Day Rolling Correlation", fontsize=10)
ax2.set_ylim(-1, 1)
ax2.legend(loc="upper right", fontsize=7.5, ncol=3)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

for label, (start, end) in REGIMES.items():
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    c = REGIME_COLORS[label]
    ax2.axvspan(s, e, alpha=0.07, color=c)
    ax2.text(s + (e - s) / 2, 0.90, label.replace("\n", " "),
             ha="center", fontsize=7, color=c, fontweight="bold")

# Panel 3: summary table
ax3.axis("off")
table_data = [
    [
        r["regime"].replace("\n", " "), str(r["n_days"]),
        f"{r['corr']:+.3f}", f"{r['avg_roll']:+.3f}",
        f"{r['min_roll']:+.3f} / {r['max_roll']:+.3f}",
        f"{r['btc_chg']:+.1f}%", f"{r['gold_chg']:+.1f}%",
    ]for r in results
]
col_labels = ["Regime", "Days", "Overall Corr", "Avg 20d Roll",
              "Min/Max Roll", "BTC Chg", "PAXG Chg"]
tbl = ax3.table(cellText=table_data, colLabels=col_labels, loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.scale(1.1, 2.0)
for j in range(len(col_labels)):
    tbl[(0, j)].set_facecolor("#264653")
    tbl[(0, j)].set_text_props(color="white", fontweight="bold")
for i, r in enumerate(results, 1):
    cv = r["corr"]
    if cv > 0.5:
        color = "#2DC653"
    elif cv > 0:
        color = "#8BC34A"
    elif cv > -0.5:
        color = "#FF9800"
    else:
        color = "#E63946"
    tbl[(i, 2)].set_facecolor(color)
    tbl[(i, 2)].set_text_props(color="white", fontweight="bold")

plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight")
print(f"Chart saved -> {OUTPUT_PNG}")
plt.show()
