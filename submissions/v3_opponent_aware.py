
"""
Kaggriculture v2.1 - Championship Agent (Validation Fixed)
Profit-per-turn optimizer with animal economy, fertilizer synergy,
market intelligence, and terminal liquidation.
"""
import math

# ============================================================================
# CONSTANTS
# ============================================================================

CROPS = {
    "WHEAT":      {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "interval": 0, "max_yield": 6, "ongoing": False, "base_price": 25, "days_occupied": 4},
    "CARROT":     {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "interval": 0, "max_yield": 4, "ongoing": False, "base_price": 35, "days_occupied": 3},
    "TOMATO":     {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "interval": 1, "max_yield": 4, "ongoing": True,  "base_price": 60, "days_occupied": 12},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True,  "base_price": 120, "days_occupied": 17},
    "MELON":      {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False, "base_price": 250, "days_occupied": 12},
}

ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG",  "product_price": 50},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK", "product_price": 160},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL", "product_price": 200},
}

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]

MARKET_I0 = 10000
PRICE_FLOOR = 1

MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "I0": MARKET_I0, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "I0": MARKET_I0, "T": 450, "below_func": "log",    "below_target": 0.20, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": MARKET_I0, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": MARKET_I0, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "I0": MARKET_I0, "T": 332, "below_func": "linear", "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": MARKET_I0, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": MARKET_I0, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

LAND_PRICES = [1000, 2000, 4000]

TURNS_PER_DAY = 24
EPISODE_STEPS = 720
SEASON_DAYS = 30
SHED_CAPACITY = 100
MAX_MARKET_ORDERS = 10

MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}

# ============================================================================
# MARKET ENGINE
# ============================================================================

def _shape(func, x):
    x = max(0.0, x)
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    return x

def market_price(item, inventory, params=None):
    p = (params or MARKET_PARAMS).get(item)
    if p is None:
        return 1
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T)
        price = base + amp * _shape(f, I0 - inventory)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T)
        price = base - amp * _shape(f, inventory - I0)
    return max(PRICE_FLOOR, int(round(price)))

def best_sell_batch(item, shed_qty, market_inventory, params=None, min_marginal_price=1):
    if shed_qty <= 0:
        return 0, 0
    inv = market_inventory
    qty = 0
    revenue = 0
    for _ in range(shed_qty):
        price = market_price(item, inv, params)
        if price < min_marginal_price:
            break
        revenue += price
        inv += 1
        qty += 1
    return qty, revenue

# ============================================================================
# STATE TRACKING
# ============================================================================

class FarmState:
    def __init__(self, obs):
        self.obs = obs
        self.farms = obs.get("farms", [])
        self.player = obs.get("player", 0)
        self.private = obs.get("private", {}) or {}
        self.market = obs.get("market", {}) or {}
        self.day = obs.get("day", 0)
        self.hour = obs.get("hour", 0)

        if not self.farms or self.player >= len(self.farms):
            self.valid = False
            return
        self.valid = True

        self.farm = self.farms[self.player]
        self.board_size = len(self.farm["tiles"])
        self.half = self.board_size // 2
        self.money = self.farm.get("money", 0)
        self.shed = self.private.get("shed", {})
        self.seeds = self.private.get("seeds", {})
        self.m_inv = self.market.get("inventory", {})
        self.m_params = self.market.get("params")

        self.turns_left = EPISODE_STEPS - (self.day * TURNS_PER_DAY + self.hour)
        self.days_left = SEASON_DAYS - self.day

        self.shed_positions = [
            (self.half - 1, self.half - 1),
            (self.half, self.half - 1),
            (self.half - 1, self.half),
            (self.half, self.half),
        ]

        self.plants = []
        self.animals = []
        self.structures = []
        self.weeds = []
        self.empty_tiles = []
        self.locked_tiles = []

        for y, row in enumerate(self.farm["tiles"]):
            for x, tile in enumerate(row):
                if tile is None:
                    self.empty_tiles.append((x, y))
                elif tile == "LOCKED":
                    self.locked_tiles.append((x, y))
                elif isinstance(tile, dict):
                    kind = tile.get("kind")
                    if kind == "PLANT":
                        self.plants.append({"pos": (x, y), "data": tile})
                    elif kind in ("COOP", "PASTURE"):
                        self.structures.append({"pos": (x, y), "data": tile})
                        if tile.get("animal"):
                            self.animals.append({"pos": (x, y), "data": tile})
                    elif kind == "WEED":
                        self.weeds.append((x, y))

        self.farmer_pos = tuple(self.farm.get("farmer", [0, 0]))
        self.hand_positions = [tuple(h) for h in self.farm.get("hands", [])]
        self.all_workers = [self.farmer_pos] + self.hand_positions

        self.land_bought = self._get_land_bought()
        self.next_land_price = self._get_next_land_price()

        # --- Opponent awareness (v3 addition) ---
        # The engine shares the full `farms` list with both players (only
        # `private`/shed/seeds/inventory is hidden) - see kaggriculture.py
        # `_initialize`: `state[i].observation.farms = farms` (same list,
        # both indices). So opponent crop/animal mix is real, legitimate
        # signal, not a guess.
        self.opp_crop_counts = {}
        self.opp_animal_counts = {}
        self.opp_money = 0
        opp_idx = 1 - self.player
        if 0 <= opp_idx < len(self.farms):
            opp_farm = self.farms[opp_idx]
            self.opp_money = opp_farm.get("money", 0)
            for row in opp_farm.get("tiles", []):
                for tile in row:
                    if isinstance(tile, dict):
                        if tile.get("kind") == "PLANT":
                            c = tile.get("crop")
                            self.opp_crop_counts[c] = self.opp_crop_counts.get(c, 0) + 1
                        elif tile.get("kind") in ("COOP", "PASTURE") and tile.get("animal"):
                            a = tile.get("animal")
                            self.opp_animal_counts[a] = self.opp_animal_counts.get(a, 0) + 1

    def _get_land_bought(self):
        unlocked = 0
        for row in self.farm["tiles"]:
            for tile in row:
                if tile != "LOCKED":
                    unlocked += 1
        if unlocked <= 25:
            return 0
        elif unlocked <= 50:
            return 1
        elif unlocked <= 75:
            return 2
        return 3

    def _get_next_land_price(self):
        idx = self.land_bought
        if idx < len(LAND_PRICES):
            return LAND_PRICES[idx]
        return None

    def dist(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_shed_pos(self, pos):
        return min(self.shed_positions, key=lambda s: self.dist(pos, s))

# ============================================================================
# TASK SYSTEM
# ============================================================================

class Task:
    def __init__(self, pos, action, value, kind, **kwargs):
        self.pos = pos
        self.action = action
        self.value = value
        self.kind = kind
        self.__dict__.update(kwargs)

def step_toward(pos, target):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    if dx == 0 and dy == 0:
        return "PASS"
    if abs(dx) >= abs(dy) and dx != 0:
        return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"

def find_survival_tasks(state):
    tasks = []
    for plant in state.plants:
        tile = plant["data"]
        pos = plant["pos"]
        if not tile.get("watered_today") and tile.get("consecutive_unwatered", 0) >= 1:
            crop = tile.get("crop", "WHEAT")
            value = CROPS.get(crop, {}).get("base_price", 25) * 10 + 5000
            tasks.append(Task(pos, "WATER", value, "survival_water", crop=crop))

    for animal in state.animals:
        tile = animal["data"]
        pos = animal["pos"]
        if not tile.get("fed_today") and tile.get("consecutive_unfed", 0) >= 1:
            animal_type = tile.get("animal", "GOOSE")
            value = ANIMALS.get(animal_type, {}).get("cost", 300) + 5000
            tasks.append(Task(pos, "FEED", value, "survival_feed", animal=animal_type))

    return tasks

def find_harvest_tasks(state, days_left):
    tasks = []
    for plant in state.plants:
        tile = plant["data"]
        pos = plant["pos"]
        yield_units = tile.get("yield_units", 0)
        if yield_units > 0:
            crop = tile.get("crop", "WHEAT")
            inv = state.m_inv.get(crop, MARKET_I0)
            price = market_price(crop, inv, state.m_params)
            revenue = yield_units * price
            if days_left <= 3:
                revenue *= 2
            tasks.append(Task(pos, "HARVEST", revenue, "harvest", crop=crop, units=yield_units))

    for animal in state.animals:
        tile = animal["data"]
        pos = animal["pos"]
        yield_units = tile.get("yield_units", 0)
        if yield_units > 0:
            animal_type = tile.get("animal", "GOOSE")
            product = ANIMALS.get(animal_type, {}).get("product", "EGG")
            inv = state.m_inv.get(product, MARKET_I0)
            price = market_price(product, inv, state.m_params)
            revenue = yield_units * price
            if days_left <= 3:
                revenue *= 2
            tasks.append(Task(pos, "HARVEST", revenue, "harvest_animal", product=product, units=yield_units))

    return tasks

def find_fertilizer_tasks(state):
    tasks = []
    for animal in state.animals:
        pos = animal["pos"]
        inv = state.m_inv.get("FERTILIZER", MARKET_I0)
        price = market_price("FERTILIZER", inv, state.m_params)
        tasks.append(Task(pos, "COLLECT_FERTILIZER", price * 0.8, "fertilizer_collect"))
    return tasks

def find_care_tasks(state):
    tasks = []
    for animal in state.animals:
        tile = animal["data"]
        pos = animal["pos"]
        if tile.get("fed_today") and not tile.get("cared_today"):
            animal_type = tile.get("animal", "GOOSE")
            product = ANIMALS.get(animal_type, {}).get("product", "EGG")
            inv = state.m_inv.get(product, MARKET_I0)
            price = market_price(product, inv, state.m_params)
            tasks.append(Task(pos, "CARE", price * 0.7, "care", animal=animal_type))
    return tasks

def find_feed_tasks(state):
    tasks = []
    for animal in state.animals:
        tile = animal["data"]
        pos = animal["pos"]
        if not tile.get("fed_today") and tile.get("consecutive_unfed", 0) == 0:
            animal_type = tile.get("animal", "GOOSE")
            value = ANIMALS.get(animal_type, {}).get("cost", 300) + 50
            tasks.append(Task(pos, "FEED", value, "feed", animal=animal_type))
    return tasks

def find_fertilize_tasks(state, days_left):
    tasks = []
    fert_in_shed = state.shed.get("FERTILIZER", 0)
    if fert_in_shed <= 0:
        return tasks

    for plant in state.plants:
        tile = plant["data"]
        pos = plant["pos"]
        crop = tile.get("crop", "WHEAT")

        if crop == "MELON":
            continue

        if tile.get("fertilized_days", 0) > 0:
            continue

        cd = CROPS.get(crop, {})
        age = tile.get("age", 0)

        if cd.get("ongoing", False):
            first_day = cd.get("first_yield_day", 999)
            if age < first_day and days_left > first_day - age + 3:
                inv = state.m_inv.get(crop, MARKET_I0)
                price = market_price(crop, inv, state.m_params)
                extra = 3 if crop == "TOMATO" else 2
                value = extra * price
                tasks.append(Task(pos, "FERTILIZE", value, "fertilize", crop=crop))
        else:
            max_day = cd.get("max_yield_day", 999)
            bonus_start = math.ceil(max_day / 2)
            if age < bonus_start and days_left > max_day - age:
                inv = state.m_inv.get(crop, MARKET_I0)
                price = market_price(crop, inv, state.m_params)
                value = 2 * price
                tasks.append(Task(pos, "FERTILIZE", value, "fertilize", crop=crop))

    return tasks

def find_water_tasks(state, days_left):
    tasks = []
    for plant in state.plants:
        tile = plant["data"]
        pos = plant["pos"]
        if not tile.get("watered_today") and tile.get("consecutive_unwatered", 0) == 0:
            crop = tile.get("crop", "WHEAT")
            cd = CROPS.get(crop, {})
            age = tile.get("age", 0)

            if not cd.get("ongoing", False):
                max_day = cd.get("max_yield_day", 999)
                bonus_start = math.ceil(max_day / 2)
                if bonus_start <= age <= max_day:
                    inv = state.m_inv.get(crop, MARKET_I0)
                    price = market_price(crop, inv, state.m_params)
                    value = price * (2 if tile.get("fertilized_days", 0) > 0 else 1)
                    tasks.append(Task(pos, "WATER", value, "water_bonus", crop=crop))
                elif days_left > 5:
                    tasks.append(Task(pos, "WATER", 5, "water_maintenance", crop=crop))
            else:
                if tile.get("fertilized_days", 0) > 0:
                    inv = state.m_inv.get(crop, MARKET_I0)
                    price = market_price(crop, inv, state.m_params)
                    tasks.append(Task(pos, "WATER", price, "water_fertilized", crop=crop))
                elif days_left > 5:
                    tasks.append(Task(pos, "WATER", 3, "water_maintenance", crop=crop))
    return tasks

def find_plant_tasks(state, days_left, money):
    tasks = []
    if days_left <= 2:
        return tasks

    candidates = []
    for crop, cd in CROPS.items():
        seed_cost = cd.get("seed", 999)
        if seed_cost > money:
            continue

        first_day = cd.get("first_yield_day", 999)
        if days_left < first_day + 1:
            continue

        max_yield = cd.get("max_yield", 0)
        base_price = cd.get("base_price", 1)

        if cd.get("ongoing", False):
            if crop == "TOMATO":
                productions = min(4, max(0, days_left - 8))
            else:
                productions = min(4, max(0, (days_left - 10) // 2 + 1))
            expected_yield = productions
        else:
            max_day = cd.get("max_yield_day", 999)
            if days_left >= max_day + 1:
                expected_yield = max_yield
            else:
                expected_yield = max(1, days_left - 1)

        gross = expected_yield * base_price
        profit = gross - seed_cost

        if crop in ["WHEAT", "CARROT"] and state.shed.get("FERTILIZER", 0) > 0:
            profit += 2 * base_price
        elif crop in ["TOMATO", "STRAWBERRY"] and state.shed.get("FERTILIZER", 0) > 0:
            if crop == "TOMATO":
                profit += 3 * base_price
            else:
                profit += 4 * base_price

        if profit > 0:
            days_occ = cd.get("days_occupied", 1)
            # v3: discount crops the opponent already has a heavy position
            # in - if we both harvest the same crop around the same time,
            # concurrent selling crashes the shared price faster than a
            # solo profit estimate accounts for. This is a real signal
            # (opponent tiles are visible), not a guess.
            opp_count = state.opp_crop_counts.get(crop, 0)
            crowding_discount = 1.0 / (1.0 + 0.15 * opp_count)
            candidates.append((profit / max(1, days_occ) * crowding_discount, profit, crop))

    candidates.sort(reverse=True)

    for profit_per_day, profit, crop in candidates:
        best_tile = None
        best_dist = 999
        for pos in state.empty_tiles:
            d = state.dist(pos, state.nearest_shed_pos(pos))
            if d < best_dist:
                best_dist = d
                best_tile = pos

        if best_tile:
            tasks.append(Task(best_tile, "PLANT", profit, "plant", crop=crop))
            break

    return tasks

def find_build_tasks(state, days_left, money):
    tasks = []
    if days_left <= 10:
        return tasks

    coops = [s for s in state.structures if s["data"].get("kind") == "COOP"]
    pastures = [s for s in state.structures if s["data"].get("kind") == "PASTURE"]
    empty_coops = [s for s in coops if not s["data"].get("animal")]
    empty_pastures = [s for s in pastures if not s["data"].get("animal")]

    geese_in_shed = state.shed.get("GOOSE", 0)
    if geese_in_shed > 0 and not empty_coops:
        for pos in state.empty_tiles:
            tasks.append(Task(pos, "BUILD_COOP", 500, "build_coop"))
            break

    cows_in_shed = state.shed.get("COW", 0)
    sheep_in_shed = state.shed.get("SHEEP", 0)
    if (cows_in_shed > 0 or sheep_in_shed > 0) and not empty_pastures:
        for pos in state.empty_tiles:
            tasks.append(Task(pos, "BUILD_PASTURE", 600, "build_pasture"))
            break

    return tasks

def find_place_animal_tasks(state, days_left):
    tasks = []
    if days_left <= 8:
        return tasks

    for animal_type, data in ANIMALS.items():
        in_shed = state.shed.get(animal_type, 0)
        if in_shed <= 0:
            continue

        structure = data.get("structure", "COOP")
        for struct in state.structures:
            if struct["data"].get("kind") == structure and not struct["data"].get("animal"):
                prod_price = data.get("product_price", 50)
                interval = data.get("interval", 1)
                expected_profit = prod_price * (days_left // max(1, interval)) * 1.5
                tasks.append(Task(struct["pos"], "PLACE", expected_profit, "place_animal", 
                                animal=animal_type, item=animal_type))
                break

    return tasks

def find_weed_tasks(state):
    tasks = []
    for pos in state.weeds:
        tasks.append(Task(pos, "DIG", 10, "weed"))
    return tasks

# ============================================================================
# MARKET ORDERS (all return tuples, NOT Task objects)
# ============================================================================

def find_sell_orders(state, days_left):
    orders = []
    for item, qty in state.shed.items():
        if qty <= 0 or item == "FERTILIZER":
            continue

        inv = state.m_inv.get(item, MARKET_I0)
        cur_price = market_price(item, inv, state.m_params)

        if days_left <= 2:
            orders.append(("SELL", item, qty))
            continue

        shed_used = sum(state.shed.values())
        shed_full = shed_used >= SHED_CAPACITY - 10

        if shed_full:
            sell_qty, _ = best_sell_batch(item, qty, inv, state.m_params, 
                                          min_marginal_price=max(PRICE_FLOOR, int(cur_price * 0.5)))
            if sell_qty > 0:
                orders.append(("SELL", item, sell_qty))
        else:
            base = MARKET_PARAMS.get(item, {}).get("base", 1)
            if cur_price >= base * 0.8:
                sell_qty = min(qty, max(1, qty // 4))
                sell_qty, _ = best_sell_batch(item, sell_qty, inv, state.m_params,
                                              min_marginal_price=max(PRICE_FLOOR, int(cur_price * 0.7)))
                if sell_qty > 0:
                    orders.append(("SELL", item, sell_qty))

    return orders

def find_buy_orders(state, money, days_left):
    orders = []

    best_crop = None
    best_profit = 0
    for crop, cd in CROPS.items():
        seed_cost = cd.get("seed", 999)
        if seed_cost > money:
            continue
        first_day = cd.get("first_yield_day", 999)
        if days_left < first_day + 1:
            continue

        max_yield = cd.get("max_yield", 0)
        base_price = cd.get("base_price", 1)
        profit = max_yield * base_price - seed_cost
        if profit > best_profit:
            best_profit = profit
            best_crop = crop

    if best_crop and state.seeds.get(best_crop, 0) < 3:
        seed_cost = CROPS[best_crop]["seed"]
        if money >= seed_cost:
            orders.append(("BUY_SEED", best_crop, 1))
            money -= seed_cost

    total_animals = len(state.animals)
    wheat_needed = total_animals * days_left
    wheat_in_shed = state.shed.get("WHEAT", 0)
    wheat_seeds = state.seeds.get("WHEAT", 0)

    if total_animals > 0 and wheat_in_shed + wheat_seeds < wheat_needed * 0.5:
        inv = state.m_inv.get("WHEAT", MARKET_I0)
        price = market_price("WHEAT", inv, state.m_params)
        buy_qty = min(5, total_animals * 2)
        cost = 0
        temp_inv = inv
        for _ in range(buy_qty):
            cost += market_price("WHEAT", temp_inv, state.m_params)
            temp_inv = max(0, temp_inv - 1)

        if money >= cost and price <= 30:
            orders.append(("BUY_PRODUCT", "WHEAT", buy_qty))
            money -= cost

    if days_left > 15 and len(state.animals) < 3:
        for animal_type in ["GOOSE", "COW", "SHEEP"]:
            data = ANIMALS.get(animal_type, {})
            cost = data.get("cost", 999)
            if cost > money:
                continue

            structure = data.get("structure", "COOP")
            has_empty = any(s["data"].get("kind") == structure and not s["data"].get("animal") 
                          for s in state.structures)

            if has_empty:
                interval = data.get("interval", 1)
                prod_price = data.get("product_price", 50)
                productions = days_left // max(1, interval)
                opp_count = state.opp_animal_counts.get(animal_type, 0)
                crowding_discount = 1.0 / (1.0 + 0.15 * opp_count)
                profit = (productions * prod_price * 1.5 - cost) * crowding_discount
                if profit > 200:
                    orders.append(("BUY_ANIMAL", animal_type, 1))
                    money -= cost
                    break

    return orders

def find_hire_orders(state, days_left):
    orders = []
    if days_left <= 3:
        return orders

    num_plants = len(state.plants)
    num_animals = len(state.animals)
    num_weeds = len(state.weeds)

    daily_actions_needed = num_plants + num_animals * 2 + num_weeds + 5
    daily_actions_available = len(state.all_workers) * 24

    hands_today = len(state.hand_positions)
    if hands_today < 5 and daily_actions_needed > daily_actions_available * 0.7:
        orders.append(("HIRE",))

    return orders

def find_land_orders(state, money, days_left):
    orders = []
    if state.next_land_price is None:
        return orders
    if state.next_land_price > money:
        return orders
    if days_left <= 10:
        return orders

    expected_value = 5 * 1420
    if expected_value > state.next_land_price:
        orders.append(("BUY_LAND",))

    return orders

# ============================================================================
# WORKER ASSIGNMENT
# ============================================================================

def assign_workers(state, tasks):
    if not tasks:
        return [None for _ in state.all_workers]

    workers = state.all_workers
    assignments = [None] * len(workers)
    used_tasks = set()

    tasks_sorted = sorted(tasks, key=lambda t: -t.value)

    for task in tasks_sorted:
        tkey = (task.pos, task.action, task.kind)
        if tkey in used_tasks:
            continue

        best_w = None
        best_score = float('inf')

        for wi, wpos in enumerate(workers):
            if assignments[wi] is not None:
                continue
            d = state.dist(wpos, task.pos)
            score = (d + 1) / max(1, task.value)
            if score < best_score:
                best_score = score
                best_w = wi

        if best_w is not None:
            assignments[best_w] = task
            used_tasks.add(tkey)

    return assignments

def task_to_action(worker_pos, task):
    if task is None:
        return ["PASS"]

    if worker_pos != task.pos:
        return [step_toward(worker_pos, task.pos)]

    if task.action == "PLANT":
        return ["PLANT", getattr(task, "crop", "WHEAT")]
    elif task.action == "PLACE":
        return ["PLACE", getattr(task, "item", "GOOSE"), 1]
    elif task.action in ("WATER", "HARVEST", "FEED", "CARE", "FERTILIZE", 
                          "COLLECT_FERTILIZER", "DIG", "BUILD_COOP", "BUILD_PASTURE"):
        return [task.action]
    else:
        return ["PASS"]

# ============================================================================
# MAIN AGENT
# ============================================================================

def agent(obs, config=None):
    state = FarmState(obs)
    if not state.valid:
        return {"farmer": ["PASS"], "hands": [], "market": []}

    days_left = state.days_left
    money = state.money

    # ========================================================================
    # PHASE 1: Market Orders (all return tuples, converted to lists)
    # ========================================================================
    market_orders = []
    orders_used = 0

    for order in find_sell_orders(state, days_left):
        if orders_used >= MAX_MARKET_ORDERS:
            break
        market_orders.append(list(order))
        orders_used += 1

    for order in find_buy_orders(state, money, days_left):
        if orders_used >= MAX_MARKET_ORDERS:
            break
        market_orders.append(list(order))
        orders_used += 1

    for order in find_hire_orders(state, days_left):
        if orders_used >= MAX_MARKET_ORDERS:
            break
        market_orders.append(list(order))
        orders_used += 1

    for order in find_land_orders(state, money, days_left):
        if orders_used >= MAX_MARKET_ORDERS:
            break
        market_orders.append(list(order))
        orders_used += 1

    # ========================================================================
    # PHASE 2: Worker Tasks
    # ========================================================================
    all_tasks = []

    all_tasks += find_survival_tasks(state)
    all_tasks += find_harvest_tasks(state, days_left)
    all_tasks += find_care_tasks(state)
    all_tasks += find_feed_tasks(state)
    all_tasks += find_fertilizer_tasks(state)
    all_tasks += find_fertilize_tasks(state, days_left)
    all_tasks += find_water_tasks(state, days_left)
    all_tasks += find_build_tasks(state, days_left, money)
    all_tasks += find_place_animal_tasks(state, days_left)
    all_tasks += find_plant_tasks(state, days_left, money)
    all_tasks += find_weed_tasks(state)

    # ========================================================================
    # PHASE 3: Assign workers
    # ========================================================================
    assignments = assign_workers(state, all_tasks)

    farmer_action = task_to_action(state.farmer_pos, assignments[0])
    hands_actions = []
    for i in range(len(state.hand_positions)):
        if i + 1 < len(assignments):
            hands_actions.append(task_to_action(state.hand_positions[i], assignments[i + 1]))
        else:
            hands_actions.append(["PASS"])

    return {
        "farmer": farmer_action,
        "hands": hands_actions,
        "market": market_orders[:MAX_MARKET_ORDERS]
    }
