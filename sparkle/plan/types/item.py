from ortools.sat.python import cp_model

from sparkle.types.item import SparkleItem
from sparkle.plan.types.recipe import SparklePlanRecipe
from sparkle.plan.types.trade_plan import SparklePlanTradePlan
from sparkle.plan.types.market_trade import SparklePlanMarketTrade


class SparklePlanItem:
    def __init__(self, model: cp_model.CpModel, inf: int,
                 data: SparkleItem, additional_qty: int,
                 market_buys: list[SparklePlanMarketTrade], market_sells: list[SparklePlanMarketTrade],
                 recipes_producing: list[SparklePlanRecipe], recipes_consuming: list[SparklePlanRecipe]):
        self.model = model
        self.inf = inf

        self.data = data
        self.additional_qty = additional_qty

        self.market_buys = market_buys
        self.market_sells = market_sells

        self.recipes_producing = recipes_producing
        self.recipes_consuming = recipes_consuming

        self.sells = [market_buy.trades for market_buy in self.market_buys]
        self.buys = [market_sell.trades for market_sell in self.market_sells]

        self.bought = self._setup_bought()
        self.cost = self._setup_cost()

        self.produced = self._setup_produced()
        self.consumed = self._setup_consumed()

        self.leftovers = self.bought + self.produced - self.consumed - self.additional_qty

        self._setup_balance()
    
    def trade_plan(self, solver: cp_model.CpSolver) -> list[SparklePlanTradePlan]:
        # TODO: move to market_trade
        return [
            SparklePlanTradePlan(self.data.item_id, solver.Value(buy_var))
            for buy_id, buy_var in enumerate(self.buys) if solver.Value(buy_var) > 0
        ]
    
    def _setup_bought(self) -> cp_model.IntVar:
        bought_var = self.model.NewIntVar(0, self.inf, f"item_bought_{self.data.item_id}")

        self.model.Add(bought_var == sum(self.buys))

        return bought_var
    
    def _setup_cost(self) -> cp_model.IntVar:
        cost_expr = [market_sell.value for market_sell in self.market_sells]
        cost_var = self.model.NewIntVar(0, self.inf, f"item_cost_{self.data.item_id}")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_produced(self) -> cp_model.IntVar:
        produced_expr = [recipe.crafts * recipe.data.produced_item.qty for recipe in self.recipes_producing]
        produced_var = self.model.NewIntVar(0, self.inf, f"item_produced_{self.data.item_id}")

        self.model.Add(produced_var == sum(produced_expr))

        return produced_var
    
    def _setup_consumed(self) -> cp_model.IntVar:
        consumed_expr = [recipe.crafts * recipe.data.consumed_qty[self.data.item_id] for recipe in self.recipes_consuming]
        consumed_var = self.model.NewIntVar(0, self.inf, f"item_consumed_{self.data.item_id}")

        self.model.Add(consumed_var == sum(consumed_expr))

        return consumed_var
    
    def _setup_balance(self) -> None:
        self.model.Add(self.bought + self.produced - self.consumed >= self.additional_qty)
