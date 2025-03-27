from collections import defaultdict
import itertools
from ortools.sat.python import cp_model

from sparkle.types.item import SparkleItem
from sparkle.types.recipe import SparkleRecipe
from sparkle.types.itemqty import SparkleItemQty
from sparkle.types.market_trade import SparkleMarketTrade
from sparkle.plan.types.item import SparklePlanItem
from sparkle.plan.types.recipe import SparklePlanRecipe
from sparkle.plan.types.trade_plan import SparklePlanTradePlan
from sparkle.plan.types.craft_plan import SparklePlanCraftPlan
from sparkle.plan.types.market_trade import SparklePlanMarketTrade

# TODO: Reverse topological pruning to remove unused items

class SparklePlan:
    def __init__(self,
                 items: list[SparkleItem],
                 recipes: dict[str, SparkleRecipe],
                 market_buys: dict[str, list[SparkleMarketTrade]],
                 market_sells: dict[str, list[SparkleMarketTrade]],
                 target: SparkleItemQty, inf=int(1e10)):
        self.model = cp_model.CpModel()

        self.target = target
        self.inf = inf

        self.items = items
        self.recipes = recipes
        self.market_buys = market_buys
        self.market_sells = market_sells

        self.plan_recipes = self._setup_plan_recipes()
        self.plan_trades = self._setup_plan_trades()

        self.plan_items = self._setup_plan_items()

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
                plan_trade.trade_plan(solver)
                for plan_trade in self.plan_trades.values()
            ))

            craft_plans = list(itertools.chain.from_iterable(
                plan_recipe.craft_plan(solver) for plan_recipe in self.plan_recipes.values()
            ))

            leftovers = [
                SparkleItemQty(item_id, solver.Value(plan_item.leftovers))
                for item_id, plan_item in self.plan_items.items()
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
    
    def _setup_plan_items(self) -> dict[str, SparklePlanItem]:
        return {
            item.item_id: SparklePlanItem(self.model, self.inf,
                                          self.plan_recipes, self.plan_trades,
                                          item,
                                          self.target.qty if item.item_id == self.target.item_id else 0)
            for item in self.items
        }
    
    def _setup_plan_recipes(self) -> dict[str, SparklePlanRecipe]:
        return {
            recipe.recipe_id: SparklePlanRecipe(self.model, self.inf, recipe)
            for recipe in self.recipes.values()
        }

    def _setup_plan_trades(self) -> dict[str, SparklePlanMarketTrade]:
        market = [*self.market_buys.values(), *self.market_sells.values()]

        return {
            trade.trade_id: SparklePlanMarketTrade(self.model, self.inf, trade)
            for market_trades in market
            for trade in market_trades
        }

    def _setup_total_cost(self):
        cost_expr = [item_var.cost for item_var in self.plan_items.values()]
        cost_var = self.model.NewIntVar(0, self.inf, "total_cost")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_total_buys(self):
        buys_expr = [
            self.plan_trades[s.trade_id].trades
            for market_sell in self.market_sells.values()
            for s in market_sell
        ]

        buys_var = self.model.NewIntVar(0, self.inf, "total_buys")

        self.model.Add(buys_var == sum(buys_expr))
        
        return buys_var

    def _setup_total_crafts(self):
        crafts_expr = [plan_recipe.crafts for plan_recipe in self.plan_recipes.values()]
        crafts_var = self.model.NewIntVar(0, self.inf, "total_crafts")

        self.model.Add(crafts_var == sum(crafts_expr))
        
        return crafts_var
