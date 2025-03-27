import pandas as pd

from sparkle.plan.plan import SparklePlan
from sparkle.itemqty import SparkleItemQty

items = ["minecraft:iron_sword", "minecraft:iron_ingot", "minecraft:stick", "minecraft:plank"]

recipes = [
    {
        "produced_item": { "item": "minecraft:iron_sword", "qty": 1 },
        "consumed_items": [
            { "item": "minecraft:iron_ingot", "qty": 2 },
            { "item": "minecraft:stick", "qty": 1 }
        ]
    },
    {
        "produced_item": { "item": "minecraft:stick", "qty": 4 },
        "consumed_items": [
            { "item": "minecraft:plank", "qty": 2 }
        ]
    }
]

market = {
    "minecraft:iron_ingot": {
        "product_id": "minecraft:iron_ingot",
        "sell_summary": [
            { "amount": -1, "pricePerUnit": 10, "orders": 1 }
        ],
        "buy_summary": [],
    },
    "minecraft:plank": {
        "product_id": "minecraft:plank",
        "sell_summary": [
            { "amount": -1, "pricePerUnit": 1, "orders": 1 }
        ],
        "buy_summary": [],
    },
}

plan = SparklePlan(
    items, recipes, market,
    SparkleItemQty("minecraft:iron_sword", 13))

def vis(plan: SparklePlan):
    min_cost, buy_plan, craft_plan, leftovers = plan.solve()

    # Build dataframe for display
    return pd.DataFrame(
        [{"step": "buy", "detail": f"{b.item_id}@{b.buy_id}", "qty": b.qty} for b in buy_plan] +
        [{"step": "craft", "detail": f"{recipes[r.recipe_id]['produced_item']['item']}#{r.recipe_id}", "qty": r.qty} for r in craft_plan] +
        [{"step": "leftover", "detail": item.item, "qty": item.qty} for item in leftovers] +
        [{"step": "total", "detail": "cost", "qty": min_cost}]
    )

print(vis(plan))