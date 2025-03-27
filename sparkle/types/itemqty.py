from dataclasses import dataclass

@dataclass
class SparkleItemQty:
    item_id: str
    qty: int

    def __repr__(self):
        return f"SparkleItemQty({self.item_id}, {self.qty})"
