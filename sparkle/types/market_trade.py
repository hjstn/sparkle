from enum import Enum
from dataclasses import dataclass


class SparkleMarketTradeType(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class SparkleMarketTrade:
    type: SparkleMarketTradeType
    trade_id: str

    item_id: str
    max_qty: int
    price: int
