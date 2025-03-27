from dataclasses import dataclass, field

from sparkle.types.recipe import SparkleRecipe
from sparkle.types.market_trade import SparkleMarketTrade


@dataclass
class SparkleItem:
    item_id: str

    market_buys: list[SparkleMarketTrade] = field(default_factory=list)
    market_sells: list[SparkleMarketTrade] = field(default_factory=list)
    
    recipes_producing: list[SparkleRecipe] = field(default_factory=list)
    recipes_consuming: list[SparkleRecipe] = field(default_factory=list)

    def __repr__(self):
        return f"SparkleItem({self.item_id}, market={len(self.market_buys), len(self.market_sells)}, recipes={len(self.recipes_producing), len(self.recipes_consuming)})"
