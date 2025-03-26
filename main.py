import pandas as pd

from sparkle.plan import SparklePlan
from sparkle.plan_itemqty import SparklePlanItemQty

items = {
    "minecraft:iron_sword": {
        "supply": [],
        "demand": []
    },
    "minecraft:iron_ingot": {
        "supply": [(-1, 10)],
        "demand": []
    },
    "minecraft:stick": {
        "supply": [(-1, 1000), (4, 1)],
        "demand": []
    },
    "minecraft:plank": {
        "supply": [(-1, 100), (2, 1)],
        "demand": []
    }
}

recipes = {
    "minecraft:iron_sword": [
        {
            "input": {
                "minecraft:iron_ingot": 2,
                "minecraft:stick": 1
            },
            "quantity": 1
        }
    ],
    "minecraft:stick": [
        {
            "input": {
                "minecraft:plank": 2
            },
            "quantity": 4
        }
    ]
}

plan = SparklePlan(
    items,
    [{
        "produced_item": SparklePlanItemQty(produced_item, recipe[0]["quantity"]),
        "consumed_items": [SparklePlanItemQty(item, qty) for item, qty in recipe[0]["input"].items()]
    }
    for produced_item, recipe in recipes.items()],
    SparklePlanItemQty("minecraft:iron_sword", 13))

def vis(plan):
    min_cost, buy_plan, craft_plan, leftovers = plan.solve()

    # Build dataframe for display
    return pd.DataFrame(
        [{"step": "buy", "detail": f"{item}@{i}", "qty": qty} for item, i, qty in buy_plan] +
        [{"step": "craft", "detail": f"{r.produced_item.item}#{r.id}", "qty": qty} for r, qty in craft_plan] +
        [{"step": "leftover", "detail": item, "qty": qty} for item, qty in leftovers.items()] +
        [{"step": "total", "detail": "cost", "qty": min_cost}]
    )

print(vis(plan))