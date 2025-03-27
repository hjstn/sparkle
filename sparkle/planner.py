from collections import defaultdict

from sparkle.types.item import SparkleItem
from sparkle.types.itemqty import SparkleItemQty
from sparkle.types.recipe import SparkleRecipe
from sparkle.types.market_trade import SparkleMarketTrade, SparkleMarketTradeType
from sparkle.plan.plan import SparklePlan

class SparklePlanner:
    def __init__(self, items: list[SparkleItem], recipes: list[SparkleRecipe], market: list[SparkleMarketTrade]):

        self.recipes = self._setup_recipes(recipes)
        self.recipes_producing, self.recipes_consuming = self._setup_recipes_auxiliary()

        self.market_buys, self.market_sells = self._setup_market(market)

        self.items = self._setup_items(items)
    
    def plan(self, target: SparkleItemQty):
        return SparklePlan(self.items, self.recipes, self.market_buys, self.market_sells, target)
    
    def _setup_recipes(self, recipes: list[SparkleRecipe]):
        return {r.recipe_id: r for r in recipes}

    def _setup_recipes_auxiliary(self):
        recipes_producing = defaultdict(list)
        recipes_consuming = defaultdict(list)
        
        for recipe in self.recipes.values():
            recipes_producing[recipe.produced_item.item_id].append(recipe)

            for consumed_item in recipe.consumed_items:
                recipes_consuming[consumed_item.item_id].append(recipe)
        
        return recipes_producing, recipes_consuming
    
    def _setup_market(self, market: list[SparkleMarketTrade]) -> tuple[dict[str, list[SparkleMarketTrade]], dict[str, list[SparkleMarketTrade]]]:
        market_buys = defaultdict(list)
        market_sells = defaultdict(list)

        for trade in market:
            if trade.type == SparkleMarketTradeType.BUY:
                market_buys[trade.item_id].append(trade)
            else:
                market_sells[trade.item_id].append(trade)

        return market_buys, market_sells

    def _setup_items(self, items: list[SparkleItem]):
        for item in items:
            item.market_buys = self.market_buys.get(item.item_id, [])
            item.market_sells = self.market_sells.get(item.item_id, [])

            item.recipes_producing = self.recipes_producing.get(item.item_id, [])
            item.recipes_consuming = self.recipes_consuming.get(item.item_id, [])

        return items
    
    def __repr__(self):
        return (
            f"SparklePlanner(\n"
            f"  items={self.items},\n"
            f"  recipes={self.recipes},\n"
            f"  market={self.market_buys, self.market_sells}\n"
            f")"
        )