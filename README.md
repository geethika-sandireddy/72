# kaggriculture-agent

Solo entry for [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)
(Kaggle simulation competition, $50K prize pool, 720-turn farming/trading game).

## Status: v0 (task-based greedy agent)

Not RL, not multi-day lookahead — a correctness-first baseline:
- Never lets a plant/animal die from neglect (exact state-transition tracking,
  matching the real engine's `consecutive_unwatered`/`consecutive_unfed` rules).
- Harvests and sells opportunistically, using **unit-by-unit price simulation**
  for sells (the real market moves price per-unit, so `qty * current_price`
  overstates revenue for any batch).
- Stops starting new investments once there's not enough season left to cash
  out (terminal liquidation awareness) and dumps remaining shed inventory in
  the final turns regardless of price, since unsold stock = $0 at turn 720.
- Greedy nearest-worker-to-highest-value-task assignment (farmer + hired hands),
  avoiding duplicate-task collisions.

**Known limitations (by design, deferred to v1/v2):**
- Single-step value scoring only — no multi-day lookahead, so it can
  underweight slow-payoff investments (land, animals) vs fast wheat/carrot.
- No opponent modeling — doesn't react to price signals as opponent behavior.
- No hiring logic yet (doesn't evaluate whether hiring a hand pays for itself).
- Movement is greedy Manhattan-distance, not route-optimized across multiple tasks.

## Results so far (8 games each, informal — not the 10-20+ Gate-2 bar yet)

| Opponent | Record | My avg score | Opponent avg score |
|---|---|---|---|
| built-in `pass` (does nothing) | 8-0-0 | ~5820 | 3000 (starting money, untouched) |
| built-in `random` | 8-0-0 | ~5800 | ~2.5 |
| built-in `starter` (carrot loop) | 8-0-0 | ~5730 | ~3497 |

These are Kaggle's own bundled reference bots (`kaggle_environments.envs.kaggriculture`),
not competitive submissions from other players — so this only proves the agent
clears the "doesn't lose to negligence" bar, not that it's leaderboard-competitive.

## Repo layout
- `agent/constants.py` — game constants, synced from the installed
  `kaggle_environments` package (crops, animals, market pricing formula).
- `agent/market.py` — unit-by-unit sell/buy price simulation.
- `agent/policy.py` — the actual decision logic.
- `submission.py` — thin Kaggle entry point wrapping `agent/policy.py`.
- `tests/` — episode runner scripts.

## Next up (v1)
Replace flat task values with proper NPV-style scoring (immediate cash +
expected future value − opportunity cost, over turns-to-complete), and add
hiring-decision logic.
