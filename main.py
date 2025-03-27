import pandas as pd

from sparkle.plan.plan import SparklePlan
from sparkle.types.item import SparkleItem
from sparkle.types.itemqty import SparkleItemQty
from sparkle.types.market_trade import SparkleMarketTrade, SparkleMarketTradeType
from sparkle.types.recipe import SparkleRecipe

items = [
    SparkleItem("minecraft:iron_sword"),
    SparkleItem("minecraft:iron_ingot"),
    SparkleItem("minecraft:stick"),
    SparkleItem("minecraft:plank")
]

recipes = [
    SparkleRecipe("r_0", SparkleItemQty("minecraft:iron_sword", 1), [
        SparkleItemQty("minecraft:iron_ingot", 2),
        SparkleItemQty("minecraft:stick", 1)
    ]),
    SparkleRecipe("r_1", SparkleItemQty("minecraft:stick", 4), [
        SparkleItemQty("minecraft:plank", 2)
    ])
]

market = [
    SparkleMarketTrade(SparkleMarketTradeType.SELL, "t_0", "minecraft:iron_ingot", -1, 10),
    SparkleMarketTrade(SparkleMarketTradeType.SELL, "t_1", "minecraft:plank", -1, 1),
]

plan = SparklePlan(items, recipes, market, SparkleItemQty("minecraft:iron_sword", 13))

def vis(plan: SparklePlan):
    min_cost, trade_plan, craft_plan, leftovers = plan.solve()

    # Build dataframe for display
    return pd.DataFrame(
        [{"step": "buy", "detail": f"{t.trade_id}", "qty": t.trades} for t in trade_plan] +
        [{"step": "craft", "detail": f"{r.recipe_id}", "qty": r.crafts} for r in craft_plan] +
        [{"step": "leftover", "detail": item.item_id, "qty": item.qty} for item in leftovers] +
        [{"step": "total", "detail": "cost", "qty": min_cost}]
    )

print(vis(plan))