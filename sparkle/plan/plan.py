from collections import defaultdict
import itertools
from ortools.sat.python import cp_model

from sparkle.plan.buy_plan import SparklePlanBuyPlan
from sparkle.plan.craft_plan import SparklePlanCraftPlan
from sparkle.plan.item import SparklePlanItem
from sparkle.itemqty import SparkleItemQty
from sparkle.plan.recipe import SparklePlanRecipe

# TODO: Reverse topological pruning to remove unused items
# TODO: Separation of Market from Item

class SparklePlan:
    def __init__(self, items: list[str], recipes: list, market: dict, target_item: SparkleItemQty, inf=int(1e10)):
        self.model = cp_model.CpModel()

        self.target_item = target_item
        self.inf = inf

        self.recipes = self._setup_recipes(recipes)
        self.recipes_producing, self.recipes_consuming = self._setup_recipes_auxiliary()

        self.market_buys, self.market_sells = self._setup_market(market)

        self.items = self._setup_items(items, target_item)

        self.total_cost = self._setup_total_cost()
        self.total_buys = self._setup_total_buys()
        self.total_crafts = self._setup_total_crafts()

    def solve(self) -> tuple[int, list[SparklePlanBuyPlan], list[SparklePlanCraftPlan], list[SparkleItemQty]]:
        self.model.Minimize(self.total_cost)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            min_cost_val = solver.Value(self.total_cost)

            buy_plans = list(itertools.chain.from_iterable(
                item_var.buy_plan(solver) for item_var in self.items.values()
            ))

            craft_plans = list(itertools.chain.from_iterable(
                recipe_var.craft_plan(solver) for recipe_var in self.recipes.values()
            ))

            leftovers = [
                SparkleItemQty(item, solver.Value(item_var.leftovers))
                for item, item_var in self.items.items()
                if solver.Value(item_var.leftovers) > 0
            ]

            return min_cost_val, buy_plans, craft_plans, leftovers
        else:
            return None, None, None, None
    
    def _setup_recipes(self, recipes: list):
        recipes = {
            recipe_id: SparklePlanRecipe(
                self.model, recipe_id, 
                SparkleItemQty(**recipe["produced_item"]),
                [SparkleItemQty(**c) for c in recipe["consumed_items"]],
                self.inf
            )
            for recipe_id, recipe in enumerate(recipes)
        }

        return recipes
    
    def _setup_recipes_auxiliary(self):
        recipes_producing = defaultdict(list)
        recipes_consuming = defaultdict(list)
        
        for recipe in self.recipes.values():
            recipes_producing[recipe.produced_item.item].append(recipe)

            for consumed_item in recipe.consumed_items:
                recipes_consuming[consumed_item.item].append(recipe)
        
        return recipes_producing, recipes_consuming


    def _setup_market(self, market: dict):
        market_buys = {
            item_id: [(b["amount"], b["pricePerUnit"]) for b in market[item_id]["buy_summary"]]
            for item_id in market
        }

        market_sells = {
            item_id: [(s["amount"], s["pricePerUnit"]) for s in market[item_id]["sell_summary"]]
            for item_id in market
        }

        return market_buys, market_sells

    def _setup_items(self, items: list, target_item: SparkleItemQty):
        return {
            item_id: self._setup_item(item_id,
                                      target_item.qty if item_id == target_item.item else 0)
            for item_id in items
        }
    
    def _setup_item(self, item_id: str, additional_qty: int):
        return SparklePlanItem(
            self.model, item_id, additional_qty,
            self.market_buys.get(item_id, []), self.market_sells.get(item_id, []),
            self.recipes_producing.get(item_id, []), self.recipes_consuming.get(item_id, []),
            self.inf
        )

    def _setup_total_cost(self):
        cost_expr = [item_var.cost for item_var in self.items.values()]
        cost_var = self.model.NewIntVar(0, self.inf, "total_cost")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_total_buys(self):
        buys_expr = [item_var.bought for item_var in self.items.values()]
        buys_var = self.model.NewIntVar(0, self.inf, "total_buys")

        self.model.Add(buys_var == sum(buys_expr))
        
        return buys_var

    def _setup_total_crafts(self):
        crafts_expr = [recipe_var.crafts for recipe_var in self.recipes.values()]
        crafts_var = self.model.NewIntVar(0, self.inf, "total_crafts")

        self.model.Add(crafts_var == sum(crafts_expr))
        
        return crafts_var