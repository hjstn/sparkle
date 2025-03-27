from dataclasses import dataclass, field

from sparkle.types.itemqty import SparkleItemQty

@dataclass
class SparkleRecipe:
    recipe_id: str
    produced_item: SparkleItemQty
    consumed_items: list[SparkleItemQty]

    consumed_qty: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        self.consumed_qty = {c.item_id: c.qty for c in self.consumed_items}

    def __repr__(self):
        return f"SparkleRecipe({self.recipe_id}, {self.produced_item}, {self.consumed_items})"
