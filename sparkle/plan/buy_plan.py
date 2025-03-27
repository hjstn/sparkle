from dataclasses import dataclass

@dataclass
class SparklePlanBuyPlan:
    item_id: str
    buy_id: int
    qty: int
