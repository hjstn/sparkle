from ortools.sat.python import cp_model

from sparkle.types.market_trade import SparkleMarketTrade
from sparkle.utils.items import parse_max_qty


class SparklePlanMarketTrade:
    def __init__(self, model: cp_model.CpModel, inf: int,
                 data: SparkleMarketTrade):
        self.model = model
        self.inf = inf

        self.data = data

        self.trades = self._setup_trades_var()
        self.value = self.data.price * self.trades
    
    def _setup_trades_var(self):
        return self.model.NewIntVar(0, parse_max_qty(self.data.max_qty, self.inf), f"market_trade_{self.data.trade_id}")
