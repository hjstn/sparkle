from ortools.sat.python import cp_model

from sparkle.plan.buy_plan import SparklePlanBuyPlan
from sparkle.plan.recipe import SparklePlanRecipe

class SparklePlanItem:
    def __init__(self, model: cp_model.CpModel, id: str, additional_qty: int,
                 market_buys: list[tuple[int, int]], market_sells: list[tuple[int, int]],
                 recipes_producing: list[SparklePlanRecipe],
                 recipes_consuming: list[SparklePlanRecipe],
                 inf: int):
        self.model = model
        self.id = id
        self.additional_qty = additional_qty

        self.market_buys = market_buys
        self.market_sells = market_sells

        self.recipes_producing = recipes_producing
        self.recipes_consuming = recipes_consuming

        self.inf = inf

        self.buys = self._setup_buy_vars()

        self.bought = self._setup_bought()
        self.cost = self._setup_cost()

        self.produced = self._setup_produced()
        self.consumed = self._setup_consumed()

        self.leftovers = self._setup_leftovers()

        self._setup_balance()
    
    def buy_plan(self, solver: cp_model.CpSolver) -> list[SparklePlanBuyPlan]:
        return [
            SparklePlanBuyPlan(self.id, buy_id, solver.Value(buy_var))
            for buy_id, buy_var in enumerate(self.buys) if solver.Value(buy_var) > 0
        ]

    def _setup_buy_vars(self) -> list[cp_model.IntVar]:
        return [
            self.model.NewIntVar(0, self._parse_max_qty(qty), f"item_buy_{self.id}_{buy_id}")
            for buy_id, (qty, _) in enumerate(self.market_sells)
        ]
    
    def _setup_bought(self) -> cp_model.IntVar:
        bought_var = self.model.NewIntVar(0, self.inf, f"item_bought_{self.id}")

        self.model.Add(bought_var == sum(self.buys))

        return bought_var
    
    def _setup_cost(self) -> cp_model.IntVar:
        cost_expr = [self.buys[buy_id] * price for buy_id, (_, price) in enumerate(self.market_sells)]
        cost_var = self.model.NewIntVar(0, self.inf, f"item_cost_{self.id}")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_produced(self) -> cp_model.IntVar:
        produced_expr = [recipe.crafts * recipe.produced_item.qty for recipe in self.recipes_producing]
        produced_var = self.model.NewIntVar(0, self.inf, f"item_produced_{self.id}")

        self.model.Add(produced_var == sum(produced_expr))

        return produced_var
    
    def _setup_consumed(self) -> cp_model.IntVar:
        consumed_expr = [recipe.crafts * recipe.consumed_qty[self.id] for recipe in self.recipes_consuming]
        consumed_var = self.model.NewIntVar(0, self.inf, f"item_consumed_{self.id}")

        self.model.Add(consumed_var == sum(consumed_expr))

        return consumed_var

    def _setup_leftovers(self) -> cp_model.IntVar:
        return self.bought + self.produced - self.consumed - self.additional_qty
    
    def _setup_balance(self) -> None:
        self.model.Add(self.bought + self.produced - self.consumed >= self.additional_qty)
    
    def _parse_max_qty(self, qty: int) -> int:
        return self.inf if qty == -1 else qty
