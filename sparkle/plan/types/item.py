from ortools.sat.python import cp_model

from sparkle.plan.types.market_trade import SparklePlanMarketTrade
from sparkle.plan.types.recipe import SparklePlanRecipe
from sparkle.types.item import SparkleItem
from sparkle.plan.types.base import SparklePlanBase


class SparklePlanItem(SparklePlanBase):
    def __init__(self, model: cp_model.CpModel, inf: int,
                 plan_recipes: dict[str, SparklePlanRecipe],
                 plan_trades: dict[str, SparklePlanMarketTrade],
                 data: SparkleItem, additional_qty: int):
        super().__init__(model, inf)

        self.plan_recipes = plan_recipes
        self.plan_trades = plan_trades

        self.data = data
        self.additional_qty = additional_qty

        self.sells = [self.plan_trades[b.trade_id].trades for b in self.data.market_buys]
        self.buys = [self.plan_trades[s.trade_id].trades for s in self.data.market_sells]

        self.bought = self._setup_bought()
        self.cost = self._setup_cost()

        self.produced = self._setup_produced()
        self.consumed = self._setup_consumed()

        self.leftovers = self.bought + self.produced - self.consumed - self.additional_qty

        self._setup_balance()

    def _setup_bought(self) -> cp_model.IntVar:
        bought_var = self.model.NewIntVar(0, self.inf, f"item_bought_{self.data.item_id}")

        self.model.Add(bought_var == sum(self.buys))

        return bought_var
    
    def _setup_cost(self) -> cp_model.IntVar:
        cost_expr = [self.plan_trades[s.trade_id].value for s in self.data.market_sells]
        cost_var = self.model.NewIntVar(0, self.inf, f"item_cost_{self.data.item_id}")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_produced(self) -> cp_model.IntVar:
        produced_expr = [
            self.plan_recipes[recipe.recipe_id].crafts * recipe.produced_item.qty
            for recipe in self.data.recipes_producing
        ]

        produced_var = self.model.NewIntVar(0, self.inf, f"item_produced_{self.data.item_id}")

        self.model.Add(produced_var == sum(produced_expr))

        return produced_var
    
    def _setup_consumed(self) -> cp_model.IntVar:
        consumed_expr = [
            self.plan_recipes[recipe.recipe_id].crafts * recipe.consumed_qty[self.data.item_id]
            for recipe in self.data.recipes_consuming
        ]

        consumed_var = self.model.NewIntVar(0, self.inf, f"item_consumed_{self.data.item_id}")

        self.model.Add(consumed_var == sum(consumed_expr))

        return consumed_var
    
    def _setup_balance(self) -> None:
        self.model.Add(self.bought + self.produced - self.consumed >= self.additional_qty)
