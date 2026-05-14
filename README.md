# BTC vs Gold Correlation Analysis

## Overview

An empirical study of the "digital gold" thesis — does Bitcoin behave like gold across different market regimes? Specifically examining whether BTC acts as an inflation hedge or safe haven asset during geopolitical crises and market regime shifts.

**Period:** August 2025 – May 2026
**Data:** Binance (BTCUSDT, PAXGUSDT) — 287 overlapping trading days
**Author:** Jonathan Ho

---

## Methodology

### Data Sources
- **BTC:** Binance `BTCUSDT` daily klines (close price)
- **Gold Proxy:** Binance `PAXGUSDT` (PAX Gold — 1 token = 1 troy oz LBMA gold, custodian-held)
- Both sourced from Binance public API — no authentication required

### Four Market Regimes
| Regime | Period | Market Character |
|---|---|---|
| 1. Pre-ATH Bull | Aug 6 – Oct 6, 2025 | BTC grinding to all-time high of $124,659 (Oct 6) |
| 2. Post-ATH Drawdown | Oct 7 – Feb 27, 2026 | BTC -45.7% from ATH; crypto risk-off, deleveraging |
| 3. Iran & US War | Feb 28 – Apr 7, 2026 | US-Israel strikes on Iran; geopolitical risk |
| 4. Post-Ceasefire | Apr 8 – May 14, 2026 | Ceasefire holds; risk-on recovery; inflation fears emerging |

### Analysis
- **Daily returns correlation** across each regime
- **20-day rolling correlation** to detect within-regime instability
- **Price indexed to 100** to compare relative performance across regimes

---

## Key Findings

### 1. Correlation is Weak Across All Regimes
| Regime | Overall Correlation | Avg Rolling (20d) |
|---|---|---|
| Pre-ATH Bull | +0.186 | +0.177 |
| Post-ATH Drawdown | +0.317 | +0.212 |
| War | +0.280 | +0.166 |
| Post-Ceasefire | +0.408 | +0.434 |

All regimes show **weak to moderate** correlation (below 0.5 threshold).

### 2. Rolling Correlation is Highly Unstable
Within every regime, the 20-day rolling correlation swings wildly:
- Pre-ATH Bull: **-0.504 to +0.727** (a 1.23 range — fully negative to strongly positive)
- Post-ATH Drawdown: **-0.341 to +0.795**
- War: **-0.040 to +0.444**
- Post-Ceasefire: **-0.025 to +0.697**

The relationship flips from negative to positive repeatedly within 20-day windows — there is **no stable, reliable correlation**.

### 3. BTC Fails the "Digital Gold" Test
| Regime | BTC Return | Gold Return | Observation |
|---|---|---|---|
| Pre-ATH Bull | +8.4% | +18.2% | Gold outperformed; BTC not acting as hedge |
| Post-ATH Drawdown | -45.7% | +32.2% | Gold rallied hard; BTC crashed — inverse behavior |
| War | +7.4% | -10.4% | BTC rose while gold fell — complete directional decoupling |
| Post-Ceasefire | +12.1% | -0.4% | BTC rallied, gold flat — divergent |

**Verdict:** BTC behaves like a risk-on volatile asset that sometimes moves with gold and sometimes against it, with no reliable pattern. The "digital gold" thesis is not supported by this data across any of the four regimes examined.

### 4. Current Period — Open Question (May 2026+)
The post-ceasefire window was mislabeled as "inflation hedge" — it was primarily a **risk-on recovery** dynamic (BTC up, gold flat/down). The **re-inflation fear narrative** is just beginning as of May 2026 with the latest CPI/PPI data releases. Whether BTC can hold its ground as an inflation hedge in the *current* environment is an **unanswered question** — the real-world test is just starting.

---

## Files
btc_gold_correlation.py    — Main analysis script
btc_gold_correlation.png   — 3-panel output chart
README.md                  — This file

## How to Run
bash
pip install pandas matplotlib requests
python btc_gold_correlation.py (1/2)

Outputs: console stats + `btc_gold_correlation.png`

---

## Limitations
- PAXGUSDT tracks LBMA gold price but is a crypto token — physical gold may behave slightly differently
- Correlations over 37–62 day windows lack statistical robustness for population inference
- Regime 4 is an ongoing, open question — monitoring continues

---

## Conclusions
1. BTC does **not** consistently correlate with gold — the relationship is weak, unstable, and regime-dependent
2. BTC behaves more like a **risk-on volatile asset** than a store of value
3. The **digital gold thesis remains unproven** in this data — gold served as a hedge *against* BTC during the worst drawdown, not alongside it
4. The current re-inflation period (May 2026+) is a **new, live experiment** — further monitoring required
