from enum import Enum
from dataclasses import dataclass


class SparkleMarketTradeType(Enum):
    BUY = "buy"
    SELL = "sell"

    def __str__(self):
        return f"{self.value}"


@dataclass
class SparkleMarketTrade:
    type: SparkleMarketTradeType
    trade_id: str

    item_id: str
    max_qty: int
    price: int

    def __repr__(self):
        return f"SparkleMarketTrade({self.type}, {self.trade_id}, {self.item_id}, {self.max_qty}, {self.price})"
