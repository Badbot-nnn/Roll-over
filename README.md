# League HQ — SportyBet AI Analyst League dashboard
Static single page (`index.html`) that reads `league.json`. No secrets, no backend.

## league.json schema (v1)
```
{ "schema_version": 1, "league": "League HQ", "updated_at": ISO-8601 with offset (shown in WAT),
  "stake": 100,                       // notional stake per ticket, used for ROI
  "bots":   [ { "id": "a01", "num": 1, "name": "Corner Accountant", "role": "analyst"|"commissioner",
                "stats": { computed by update.py: xp, rank, tier, streak, best_streak, wins, losses,
                           win_rate_30d (% or null), roi (% or null), shield (bool) } } ],
  "tickets":[ { "bot": "a01", "date": "YYYY-MM-DD" (WAT), "odds": 2.04,
                "result": "pending"|"won"|"lost", "booking_code": "ABC123" (optional),
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

## Scoring (in update.py)
Win: 100·ln(odds)/ln(2.5) × streak mult (1.25 ≥3, 1.5 ≥7, 2.0 ≥14) × tier (Hot 1.1, Cold 0.8) + milestone (+150 @3, +500 & Shield @7, +1500 @14).
Loss: −60·ln(odds)/ln(2.5). A Shield absorbs one loss (streak kept) and expires 14 days after earned. XP floors at 0.
Ranks: Rookie 0 · Pro Strategist 1000 · Master Predictor 4000 + best streak ≥7 · Legendary Oracle 10000 + best streak ≥14 + ROI>0.
Tier: Hot streak ≥5 · Cold loss within 48h · else Normal. Sort: streak, 30d win%, ROI.
