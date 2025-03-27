from ortools.sat.python import cp_model

from sparkle.types.market_trade import SparkleMarketTrade
from sparkle.plan.types.base import SparklePlanBase
from sparkle.plan.types.trade_plan import SparklePlanTradePlan
from sparkle.utils.items import parse_max_qty


class SparklePlanMarketTrade(SparklePlanBase):
    def __init__(self, model: cp_model.CpModel, inf: int, data: SparkleMarketTrade):
        super().__init__(model, inf)

        self.data = data

        self.trades = self._setup_trades_var()
        self.value = self.data.price * self.trades

    def trade_plan(self, solver: cp_model.CpSolver) -> list[SparklePlanTradePlan]:
        if solver.Value(self.trades) == 0:
            return []

        return [SparklePlanTradePlan(self.data.trade_id, solver.Value(self.trades))]
    
    def _setup_trades_var(self):
        return self.model.NewIntVar(0, parse_max_qty(self.data.max_qty, self.inf), f"market_trade_{self.data.trade_id}")
