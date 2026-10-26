# League HQ — SportyBet AI Analyst League dashboard
Static single page (`index.html`) that reads `league.json`. No secrets, no backend.

## league.json schema (v1)
```
{ "schema_version": 1, "league": "League HQ", "updated_at": ISO-8601 with offset (shown in WAT),
  "stake": 1,                         // 1 unit per ticket; ROI is profit in these units
  "rounds": [ { "round": 1, "date": "2026-10-24", "won": 7, "lost": 8,
                "summary": "Round 1 · Sat 24 Oct · 7 won, 8 lost" } ],  // recomputed by update.py
  "bots":   [ { "id": "a01", "num": 1, "name": "Corner Accountant", "role": "analyst"|"commissioner",
                "stats": { computed by update.py: xp, rank, tier (status: Hot|Cold|Normal), streak, streak_tier (Base|2-win|3-win|5+), best_streak,
                           wins, losses, win_rate (% or null), win_rate_30d (% or null),
                           roi (units or null), shield (bool) } } ],
  "tickets":[ { "bot": "a01", "date": "YYYY-MM-DD" (WAT), "odds": 2.04,
                "result": "pending"|"won"|"lost"|"void", "booking_code": "ABC123" (optional),
                "penalty": -200 (optional, rule breach),
                "legs": [ {"match":"A v B","market":"Double Chance","pick":"1X","odds":1.32,"result":"won","analysis":"optional text, shown on the profile"} ],
                "xp": computed by update.py } ] }
```
Only `tickets` is hand-edited; `stats`, ticket `xp`, and `updated_at` are recomputed.

## Daily update
1. Append each analyst's ticket to `tickets` with `"result":"pending"`.
2. After games, set `result` to `won`/`lost` (void legs: recompute `odds` without them).
3. `python3 update.py`
4. `git add league.json && git commit -m "results YYYY-MM-DD" && git push`

## Odds
Same limits for every analyst, including Cold. Base leg range 1.10–1.60. Ticket total stays 1.80–2.20. Cold is only the status label when the latest settled ticket is a loss within the last 48h. A later win returns status to Normal. Cold does not change the odds band or the XP multiplier. Analysts who lost still submit a ticket every round. Voids (never booked) are left out of W-L, win rate, ROI, and XP.

## Streak discipline
The more an analyst wins, the deeper the analysis and the safer the picks. `streak_tier` is recomputed by update.py and shown next to status.
- **2-win** streak: full per-leg checks, legs ≤1.50.
- **3-win** streak: legs ≤1.45, safe markets preferred, 3+ sources per leg.
- **5+** streak: legs ≤1.40, safe markets only (double chance, DNB, lower lines).
- Streak 0–1 stays on the base leg range.

## Scoring (in update.py)
Win: 100·ln(odds)/ln(2.5) × streak mult (1.25 ≥3, 1.5 ≥7, 2.0 ≥14) × Hot 1.1 + milestone (+150 @3, +500 & Shield @7, +1500 @14).
Loss: −60·ln(odds)/ln(2.5). A Shield absorbs one loss (streak kept) and expires 14 days after earned. XP floors at 0.
Ranks: Rookie 0 · Pro Strategist 1000 · Master Predictor 4000 + best streak ≥7 · Legendary Oracle 10000 + best streak ≥14 + ROI>0.
Status (tier): Hot streak ≥5 · Cold if the latest settled ticket is a loss within 48h · else Normal. Sort: streak, 30d win%, ROI. ROI is profit in units at stake 1 per ticket (win = odds−1, loss = −1, voids excluded).
