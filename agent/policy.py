"""
Kaggriculture agent v0.

Design (see notes/DESIGN.md for the full reasoning trail):
  - Every turn, build a list of candidate TASKS (things a worker could do:
    water a dying plant, harvest a ready tile, plant a new seed, etc.)
  - Score each task by estimated $ value, with harsh penalties for letting
    something die and near-zero score for anything that can't pay off
    before the season ends (terminal liquidation awareness).
  - Greedily assign workers to their best reachable task, one worker per
    task (prevents two workers colliding on the same PLANT command).
  - Market orders (sell/buy) are queued separately each turn using
    unit-by-unit price simulation so we don't crash our own prices.

This is NOT multi-day lookahead or opponent modeling — that's v2. This is
the "correct, non-negligent, exploits obvious ROI differences" baseline.
"""
from . import constants as C
from . import market as M

MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}

# Below this many remaining turns, stop starting anything that can't cash
# out in time. Computed per-candidate against days_left, not just a flat
# number, but this is the hard backstop.
SAFETY_MARGIN_TURNS = 6


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _step_toward(pos, target):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    if dx == 0 and dy == 0:
        return "PASS"
    # Move along the axis with the larger gap first (irrelevant for cost
    # since it's Manhattan distance either way, but keeps behavior stable).
    if abs(dx) >= abs(dy) and dx != 0:
        return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"


def _turns_left(day, hour):
    return C.EPISODE_STEPS - (day * C.TURNS_PER_DAY + hour)


def _days_left(day):
    return C.SEASON_DAYS - day


def _quadrant_of(x, y, board_size):
    half = board_size // 2
    if x < half and y < half: return "NW"
    if x >= half and y < half: return "NE"
    if x < half and y >= half: return "SW"
    return "SE"


def _worker_positions(farm):
    positions = [tuple(farm["farmer"])]
    positions += [tuple(h) for h in farm.get("hands", [])]
    return positions


def _find_survival_tasks(farm, board_size):
    """Anything that dies tonight if ignored. Highest priority, always."""
    tasks = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT" and not tile.get("watered_today") \
               and tile.get("consecutive_unwatered", 0) >= 1:
                tasks.append({"pos": (x, y), "action": "WATER", "value": 5000, "kind": "survival"})
            elif tile.get("kind") in ("COOP", "PASTURE") and tile.get("animal") \
                 and not tile.get("fed_today") and tile.get("consecutive_unfed", 0) >= 1:
                tasks.append({"pos": (x, y), "action": "FEED", "value": 5000, "kind": "survival"})
    return tasks


def _find_harvest_tasks(farm):
    tasks = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            if tile.get("yield_units", 0) > 0:
                # Rough value: units * a conservative product base price.
                # (Real revenue is computed properly at sell time via market.py;
                # this is only used to rank harvest vs other tasks.)
                if tile["kind"] == "PLANT":
                    item = tile["crop"]
                else:
                    item = C.ANIMALS[tile["animal"]]["product"]
                est_price = C.MARKET_PARAMS[item]["base"]
                tasks.append({
                    "pos": (x, y), "action": "HARVEST",
                    "value": tile["yield_units"] * est_price * 0.9,
                    "kind": "harvest",
                })
    return tasks


def _find_water_tasks(farm):
    """Plants not yet dying but unwatered today — worth doing if nothing
    more urgent, since watering during the bonus window adds yield."""
    tasks = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                tasks.append({"pos": (x, y), "action": "WATER", "value": 15, "kind": "water"})
    return tasks


def _find_care_tasks(farm):
    tasks = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE") \
               and tile.get("animal") and tile.get("fed_today") and not tile.get("cared_today"):
                tasks.append({"pos": (x, y), "action": "CARE", "value": 10, "kind": "care"})
    return tasks


def _best_crop_to_plant(money, days_left, turns_left):
    """ROI-ranked crop choice, filtered by whether it can pay off before
    season end (terminal liquidation awareness)."""
    candidates = []
    for crop, cd in C.CROPS.items():
        if cd["seed"] > money:
            continue
        # A crop needs first_yield_day days to pay anything, plus ~1 day
        # margin to travel+harvest+sell. If that doesn't fit, skip it.
        if days_left < cd["first_yield_day"] + 1:
            continue
        est_price = C.MARKET_PARAMS[crop]["base"]
        # crude total value estimate: max_yield * price, discounted if it's
        # an ongoing crop that likely won't reach full scheduled yields
        # given remaining days.
        value = cd["max_yield"] * est_price
        payoff_days = max(cd["max_yield_day"], cd["first_yield_day"])
        roi_per_day = (value - cd["seed"]) / max(1, payoff_days)
        candidates.append((roi_per_day, crop))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _find_empty_tiles(farm, board_size):
    empties = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if tile is None:
                empties.append((x, y))
    return empties


def agent(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    market = obs.get("market", {}) or {}
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)

    if not farms or player >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}

    farm = farms[player]
    board_size = len(farm["tiles"])
    money = farm["money"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    m_inv = market.get("inventory", {})
    m_params = market.get("params")

    turns_left = _turns_left(day, hour)
    days_left = _days_left(day)
    in_liquidation = turns_left <= SAFETY_MARGIN_TURNS * 4  # last ~1 day: stop investing

    # ---------- MARKET ORDERS (sell shed inventory, price-aware) ----------
    market_orders = []
    orders_used = 0
    max_orders = 10
    for item, qty in shed.items():
        if qty <= 0 or orders_used >= max_orders:
            continue
        inv = m_inv.get(item, C.MARKET_I0)
        cur_price = C.market_price(item, inv, m_params)
        # Don't crash the price selling our own batch: stop once marginal
        # price drops below 60% of the pre-sale price (tunable), UNLESS
        # we're in end-game liquidation, where anything above the floor
        # is worth taking since unsold stock is worth exactly $0 at turn 720.
        floor = C.PRICE_FLOOR if in_liquidation else max(C.PRICE_FLOOR, int(cur_price * 0.6))
        sell_qty, _ = M.best_sell_batch(item, qty, inv, m_params, min_marginal_price=floor)
        if sell_qty > 0:
            market_orders.append(["SELL", item, sell_qty])
            orders_used += 1

    # Buy seed for next planting decision (decided below) happens after we
    # know what workers will need; kept simple here — see planting task.

    # ---------- BUILD TASK LIST ----------
    tasks = _find_survival_tasks(farm, board_size)
    tasks += _find_harvest_tasks(farm)
    tasks += _find_care_tasks(farm)
    if not in_liquidation:
        tasks += _find_water_tasks(farm)

    # Planting: only propose if not in liquidation and there's an empty tile
    # and we can afford + have runway to profit.
    if not in_liquidation:
        crop = _best_crop_to_plant(money, days_left, turns_left)
        empties = _find_empty_tiles(farm, board_size)
        if crop and empties:
            need_seed = seeds.get(crop, 0) <= 0
            if need_seed and money >= C.CROPS[crop]["seed"] and orders_used < max_orders:
                market_orders.append(["BUY_SEED", crop, 1])
                orders_used += 1
            if seeds.get(crop, 0) > 0 or need_seed:
                # Plant on the nearest empty tile (task list picks nearest worker anyway)
                tasks.append({"pos": empties[0], "action": "PLANT", "crop": crop,
                               "value": 40, "kind": "plant"})

    # ---------- ASSIGN WORKERS TO TASKS (greedy, nearest-highest-value) --
    workers = _worker_positions(farm)
    assigned = [None] * len(workers)
    used_tasks = set()

    # Sort tasks by value desc so high-value tasks get first pick of nearest worker
    tasks.sort(key=lambda t: -t["value"])
    for t in tasks:
        tkey = t["pos"]
        if tkey in used_tasks:
            continue
        # find nearest unassigned worker
        best_w, best_d = None, None
        for wi, wpos in enumerate(workers):
            if assigned[wi] is not None:
                continue
            d = _dist(wpos, t["pos"])
            if best_d is None or d < best_d:
                best_w, best_d = wi, d
        if best_w is None:
            break
        assigned[best_w] = t
        used_tasks.add(tkey)

    # ---------- CONVERT ASSIGNMENTS TO ACTIONS ----------
    def action_for(wi):
        t = assigned[wi]
        wpos = workers[wi]
        if t is None:
            return ["PASS"]
        if wpos != t["pos"]:
            return [_step_toward(wpos, t["pos"])]
        if t["action"] == "PLANT":
            return ["PLANT", t["crop"]]
        return [t["action"]]

    farmer_action = action_for(0)
    hands_actions = [action_for(i) for i in range(1, len(workers))]

    return {"farmer": farmer_action, "hands": hands_actions, "market": market_orders[:max_orders]}
