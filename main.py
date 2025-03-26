from sparkle.sparkle import SparklePlan
import pandas as pd

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
        "supply": [(-1, 1000)],
        "demand": []
    },
    "minecraft:plank_a": {
        "supply": [(-1, 100), (2, 1)],
        "demand": []
    },
    "minecraft:plank_b": {
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
                "minecraft:plank_a": 2
            },
            "quantity": 4
        },
        {
            "input": {
                "minecraft:plank_b": 2
            },
            "quantity": 4
        }
    ]
}

sparkle_plan = SparklePlan(items, recipes, "minecraft:iron_sword", 13)

min_cost, buy_plan, craft_plan, leftovers = sparkle_plan.solve()

# Build dataframe for display
df = pd.DataFrame(
    [{"step": "buy", "detail": f"{item}@{i}", "qty": qty} for item, i, qty in buy_plan] +
    [{"step": "craft", "detail": f"{item}#{r_id}", "qty": qty} for item, r_id, qty in craft_plan] +
    [{"step": "leftover", "detail": item, "qty": qty} for item, qty in leftovers.items()]
)

print(df)