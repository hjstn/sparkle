from collections import defaultdict
import itertools
from ortools.sat.python import cp_model

from sparkle.types.item import SparkleItem
from sparkle.types.recipe import SparkleRecipe
from sparkle.types.itemqty import SparkleItemQty
from sparkle.types.market_trade import SparkleMarketTrade, SparkleMarketTradeType
from sparkle.plan.types.item import SparklePlanItem
from sparkle.plan.types.recipe import SparklePlanRecipe
from sparkle.plan.types.trade_plan import SparklePlanTradePlan
from sparkle.plan.types.craft_plan import SparklePlanCraftPlan
from sparkle.plan.types.market_trade import SparklePlanMarketTrade

# TODO: Reverse topological pruning to remove unused items
# TODO: Separation of Market from Item

class SparklePlan:
    def __init__(self, items: list[SparkleItem], recipes: list[SparkleRecipe], market: list[SparkleMarketTrade], target: SparkleItemQty, inf=int(1e10)):
        self.model = cp_model.CpModel()

        self.target = target
        self.inf = inf

        self.recipes = self._setup_recipes(recipes)
        self.recipes_producing, self.recipes_consuming = self._setup_recipes_auxiliary()

        self.market_buys, self.market_sells = self._setup_market(market)

        self.items = self._setup_items(items, target)

        self.total_cost = self._setup_total_cost()
        self.total_buys = self._setup_total_buys()
        self.total_crafts = self._setup_total_crafts()

    def solve(self) -> tuple[int, list[SparklePlanTradePlan], list[SparklePlanCraftPlan], list[SparkleItemQty]]:
        self.model.Minimize(self.total_cost)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            min_cost_val = solver.Value(self.total_cost)

            trade_plan = list(itertools.chain.from_iterable(
                item_var.trade_plan(solver) for item_var in self.items.values()
            ))

            craft_plans = list(itertools.chain.from_iterable(
                recipe_var.craft_plan(solver) for recipe_var in self.recipes.values()
            ))

            leftovers = [
                SparkleItemQty(item, solver.Value(item_var.leftovers))
                for item, item_var in self.items.items() if solver.Value(item_var.leftovers) > 0
            ]

            return min_cost_val, trade_plan, craft_plans, leftovers
        else:
            # Add more informative error handling
            status_name = {
                cp_model.UNKNOWN: "UNKNOWN",
                cp_model.MODEL_INVALID: "MODEL_INVALID",
                cp_model.INFEASIBLE: "INFEASIBLE",
                cp_model.OPTIMAL: "OPTIMAL",
                cp_model.FEASIBLE: "FEASIBLE",
            }.get(status, f"UNKNOWN_STATUS_{status}")
            
            raise RuntimeError(f"Solver failed with status: {status_name}")
    
    def _setup_recipes(self, recipes: list[SparkleRecipe]):
        recipes = {
            r.recipe_id: SparklePlanRecipe(self.model, self.inf, r)
            for r in recipes
        }

        return recipes
    
    def _setup_recipes_auxiliary(self):
        recipes_producing = defaultdict(list)
        recipes_consuming = defaultdict(list)
        
        for recipe in self.recipes.values():
            recipes_producing[recipe.data.produced_item.item_id].append(recipe)

            for consumed_item in recipe.data.consumed_items:
                recipes_consuming[consumed_item.item_id].append(recipe)
        
        return recipes_producing, recipes_consuming


    def _setup_market(self, market: list[SparkleMarketTrade]):
        market_buys = defaultdict(list)
        market_sells = defaultdict(list)

        for trade in market:
            plan_trade = SparklePlanMarketTrade(self.model, self.inf, trade)

            if trade.type == SparkleMarketTradeType.BUY:
                market_buys[trade.item_id].append(plan_trade)
            else:
                market_sells[trade.item_id].append(plan_trade)

        return market_buys, market_sells

    def _setup_items(self, items: list[SparkleItem], target: SparkleItemQty):
        return {
            i.item_id: SparklePlanItem(self.model, self.inf,
                                       i, target.qty if i.item_id == target.item_id else 0,
                                       self.market_buys.get(i.item_id, []), self.market_sells.get(i.item_id, []),
                                       self.recipes_producing.get(i.item_id, []), self.recipes_consuming.get(i.item_id, []))
            for i in items
        }

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
