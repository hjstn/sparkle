from dataclasses import dataclass


@dataclass
class SparklePlanTradePlan:
    trade_id: str
    trades: int
