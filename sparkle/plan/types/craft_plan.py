from dataclasses import dataclass


@dataclass
class SparklePlanCraftPlan:
    recipe_id: str
    crafts: int
