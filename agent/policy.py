"""
Kaggriculture agent v1.

Builds on v0 (see git history / notes/DESIGN.md for that reasoning trail).
v1 closes three gaps v0 never touched at all:
  1. HIRE - v0 never hired a farm hand, leaving worker-throughput on the
     table whenever there was more work than one farmer could do in a day.
  2. BUY_LAND - v0 never expanded land, even when the starting quadrant
     was fully utilized and capital was sitting idle.
  3. Animal investment - v0 could feed/harvest an animal if one existed,
     but never actually built a coop/pasture, bought an animal, carried it
     from the shed, and placed it. That's a real 4-step pipeline
     (BUILD -> BUY_ANIMAL -> PICKUP -> PLACE), implemented here as a
     state machine re-derived from the observation every turn (the agent
     itself is stateless between turns, by design - Kaggle calls agent(obs)
     fresh each turn with no persistent memory).

Still NOT doing: multi-day lookahead, opponent modeling. Task values below
are still single-step estimates, just no longer blind to entire action
categories the way v0's were.
"""
from . import constants as C
from . import market as M

MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
SAFETY_MARGIN_TURNS = 6
MAX_ANIMALS_V1 = 4           # cap ambition for v1 - avoid overcommitting to a
                              # pipeline we haven't proven yet on a real ladder
ANIMAL_PRIORITY = ["GOOSE", "COW", "SHEEP"]  # cheap entry first, then better payback


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _step_toward(pos, target):
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    if dx == 0 and dy == 0:
        return "PASS"
    if abs(dx) >= abs(dy) and dx != 0:
        return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"


def _turns_left(day, hour):
    return C.EPISODE_STEPS - (day * C.TURNS_PER_DAY + hour)


def _days_left(day):
    return C.SEASON_DAYS - day


def _worker_positions(farm):
    return [tuple(farm["farmer"])] + [tuple(h) for h in farm.get("hands", [])]


def _shed_adjacent_tile(board_size):
    half = board_size // 2
    return (half - 1, half - 1)  # always valid: NW quadrant is always unlocked


def _find_survival_tasks(farm):
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
            if not isinstance(tile, dict) or tile.get("yield_units", 0) <= 0:
                continue
            item = tile["crop"] if tile["kind"] == "PLANT" else C.ANIMALS[tile["animal"]]["product"]
            est_price = C.MARKET_PARAMS[item]["base"]
            tasks.append({"pos": (x, y), "action": "HARVEST",
                           "value": tile["yield_units"] * est_price * 0.9, "kind": "harvest"})
    return tasks


def _find_water_tasks(farm):
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


def _best_crop_to_plant(money, days_left):
    candidates = []
    for crop, cd in C.CROPS.items():
        if cd["seed"] > money or days_left < cd["first_yield_day"] + 1:
            continue
        est_price = C.MARKET_PARAMS[crop]["base"]
        value = cd["max_yield"] * est_price
        payoff_days = max(cd["max_yield_day"], cd["first_yield_day"])
        roi_per_day = (value - cd["seed"]) / max(1, payoff_days)
        candidates.append((roi_per_day, crop))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _find_empty_tiles(farm):
    return [(x, y) for y, row in enumerate(farm["tiles"]) for x, t in enumerate(row) if t is None]


def _animal_structure_state(farm):
    """Returns (counts_by_animal, empty_coop_pos, empty_pasture_pos)."""
    counts = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    empty_coop, empty_pasture = None, None
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "COOP":
                if tile.get("animal"):
                    counts["GOOSE"] += 1
                elif empty_coop is None:
                    empty_coop = (x, y)
            elif tile.get("kind") == "PASTURE":
                if tile.get("animal"):
                    counts[tile["animal"]] += 1
                elif empty_pasture is None:
                    empty_pasture = (x, y)
    return counts, empty_coop, empty_pasture


def _decide_animal_target(farm, money, days_left):
    counts, empty_coop, empty_pasture = _animal_structure_state(farm)
    total = sum(counts.values())
    if total >= MAX_ANIMALS_V1 or days_left < 6:
        return None, empty_coop, empty_pasture
    for animal in ANIMAL_PRIORITY:
        cd = C.ANIMALS[animal]
        if counts[animal] == 0 and money >= cd["cost"] + 100:
            return animal, empty_coop, empty_pasture
    if money >= C.ANIMALS["GOOSE"]["cost"] + 200:
        return "GOOSE", empty_coop, empty_pasture
    return None, empty_coop, empty_pasture


def _consider_buy_land(farm, money, days_left):
    unlocked = farm.get("unlocked_quadrants", ["NW"])
    n_extra = len(unlocked) - 1
    if n_extra >= len(C.LAND_ORDER) or days_left < 8:
        return False
    price = C.LAND_PRICES[n_extra]
    if money < price + 500:
        return False
    total_unlocked = occupied = 0
    for row in farm["tiles"]:
        for tile in row:
            if tile != "LOCKED":
                total_unlocked += 1
                if tile is not None:
                    occupied += 1
    return total_unlocked > 0 and (occupied / total_unlocked) > 0.75


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
    inventories = private.get("inventories", [])
    m_inv = market.get("inventory", {})
    m_params = market.get("params")

    turns_left = _turns_left(day, hour)
    days_left = _days_left(day)
    in_liquidation = turns_left <= SAFETY_MARGIN_TURNS * 4

    market_orders = []
    orders_used = 0
    max_orders = 10

    # ---------- SELL shed inventory, price-aware ----------
    for item, qty in shed.items():
        if qty <= 0 or orders_used >= max_orders or item in ("GOOSE", "COW", "SHEEP"):
            continue  # animals waiting in shed to be placed are not for sale
        inv = m_inv.get(item, C.MARKET_I0)
        cur_price = C.market_price(item, inv, m_params)
        floor = C.PRICE_FLOOR if in_liquidation else max(C.PRICE_FLOOR, int(cur_price * 0.6))
        sell_qty, _ = M.best_sell_batch(item, qty, inv, m_params, min_marginal_price=floor)
        if sell_qty > 0:
            market_orders.append(["SELL", item, sell_qty])
            orders_used += 1

    # ---------- BUILD TASK LIST ----------
    tasks = _find_survival_tasks(farm)
    tasks += _find_harvest_tasks(farm)
    tasks += _find_care_tasks(farm)
    if not in_liquidation:
        tasks += _find_water_tasks(farm)

    # ---- Planting ----
    if not in_liquidation:
        crop = _best_crop_to_plant(money, days_left)
        empties = _find_empty_tiles(farm)
        if crop and empties:
            need_seed = seeds.get(crop, 0) <= 0
            if need_seed and money >= C.CROPS[crop]["seed"] and orders_used < max_orders:
                market_orders.append(["BUY_SEED", crop, 1])
                orders_used += 1
            if seeds.get(crop, 0) > 0 or need_seed:
                tasks.append({"pos": empties[0], "action": "PLANT", "crop": crop,
                               "value": 45, "kind": "plant"})

    # ---- Animal investment pipeline (v1 addition) ----
    if not in_liquidation:
        target_animal, empty_coop, empty_pasture = _decide_animal_target(farm, money, days_left)
        if target_animal:
            structure = C.ANIMALS[target_animal]["structure"]
            empty_structure = empty_coop if structure == "COOP" else empty_pasture
            if empty_structure is None:
                empties = _find_empty_tiles(farm)
                if empties:
                    op = "BUILD_COOP" if structure == "COOP" else "BUILD_PASTURE"
                    tasks.append({"pos": empties[0], "action": op, "value": 60, "kind": "build"})
            else:
                shed_qty = shed.get(target_animal, 0)
                carrying_worker = None
                for wi, winv in enumerate(inventories):
                    if isinstance(winv, dict) and winv.get(target_animal, 0) > 0:
                        carrying_worker = wi
                        break
                if carrying_worker is not None:
                    tasks.append({"pos": empty_structure, "action": "PLACE", "item": target_animal,
                                   "value": 80, "kind": "place", "restrict_worker": carrying_worker})
                elif shed_qty > 0:
                    tasks.append({"pos": _shed_adjacent_tile(board_size), "action": "PICKUP",
                                   "item": target_animal, "value": 70, "kind": "pickup"})
                elif money >= C.ANIMALS[target_animal]["cost"] and orders_used < max_orders:
                    market_orders.append(["BUY_ANIMAL", target_animal, 1])
                    orders_used += 1

    # ---- Land expansion (v1 addition) ----
    if not in_liquidation and orders_used < max_orders and _consider_buy_land(farm, money, days_left):
        market_orders.append(["BUY_LAND"])
        orders_used += 1

    # ---------- ASSIGN WORKERS TO TASKS ----------
    workers = _worker_positions(farm)
    assigned = [None] * len(workers)
    used_tasks = set()

    tasks.sort(key=lambda t: -t["value"])
    for t in tasks:
        tkey = (t["pos"], t.get("action"))
        if tkey in used_tasks:
            continue
        restrict = t.get("restrict_worker")
        candidate_indices = [restrict] if restrict is not None else range(len(workers))
        best_w, best_d = None, None
        for wi in candidate_indices:
            if wi >= len(workers) or assigned[wi] is not None:
                continue
            d = _dist(workers[wi], t["pos"])
            if best_d is None or d < best_d:
                best_w, best_d = wi, d
        if best_w is None:
            continue
        assigned[best_w] = t
        used_tasks.add(tkey)

    # ---- HIRE decision (v1 addition): only once we've seen we can't cover
    # today's backlog with current workers, and only if it pays for itself
    # in the runway remaining.
    uncovered = sum(1 for t in tasks if (t["pos"], t.get("action")) not in used_tasks)
    if not in_liquidation and days_left >= 3 and uncovered > 0 and len(workers) < 4:
        hire_cost = C.fib_cost(farm.get("hires_today", 0) + 1)
        if money >= hire_cost + 200 and orders_used < max_orders:
            market_orders.append(["HIRE"])
            orders_used += 1

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
        if t["action"] in ("PLACE", "PICKUP"):
            return [t["action"], t["item"]]
        return [t["action"]]

    farmer_action = action_for(0)
    hands_actions = [action_for(i) for i in range(1, len(workers))]

    return {"farmer": farmer_action, "hands": hands_actions, "market": market_orders[:max_orders]}
