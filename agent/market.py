"""Market valuation helpers — sell revenue must be simulated unit-by-unit,
since the real engine moves price after every single unit sold (see
kaggriculture.py: orders processed one unit at a time, concurrently across
players). Pretending revenue = qty * current_price overstates value for any
batch beyond ~1 unit, especially for low-T items like MELON/WOOL/STRAWBERRY.
"""
from . import constants as C


def simulate_sell_revenue(item, quantity, market_inventory, params=None, max_qty=None):
    """Returns (total_revenue, revenue_per_unit_curve) for selling `quantity`
    units of `item`, walking the price down one unit at a time exactly like
    the real engine does. Cheap: O(quantity), fine for shed-sized batches.
    """
    if quantity <= 0:
        return 0, []
    inv = market_inventory
    total = 0
    curve = []
    n = quantity if max_qty is None else min(quantity, max_qty)
    for _ in range(n):
        price = C.market_price(item, inv, params)
        total += price
        curve.append(price)
        inv += 1  # selling adds to market inventory (moves toward glut)
    return total, curve


def best_sell_batch(item, shed_qty, market_inventory, params=None, min_marginal_price=1):
    """Find the largest quantity worth selling right now: keep adding units
    while the marginal (next-unit) price stays >= min_marginal_price.
    Returns (qty_to_sell, expected_revenue).
    Use min_marginal_price > floor to avoid dumping the whole shed into a
    single crashed order — e.g. pass current price * 0.5 as a floor to stop
    once you've pushed the price down by half.
    """
    if shed_qty <= 0:
        return 0, 0
    inv = market_inventory
    qty = 0
    revenue = 0
    for _ in range(shed_qty):
        price = C.market_price(item, inv, params)
        if price < min_marginal_price:
            break
        revenue += price
        inv += 1
        qty += 1
    return qty, revenue


def buy_cost(item, quantity, market_inventory, params=None):
    """Mirror of simulate_sell_revenue but for BUY_PRODUCT (wheat/fertilizer
    only). Buying drains inventory (moves toward scarcity), raising price.
    """
    if quantity <= 0:
        return 0
    inv = market_inventory
    total = 0
    for _ in range(quantity):
        price = C.market_price(item, inv, params)
        total += price
        inv = max(0, inv - 1)
    return total
