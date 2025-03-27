from ortools.sat.python import cp_model

from sparkle.plan.craft_plan import SparklePlanCraftPlan
from sparkle.itemqty import SparkleItemQty

class SparklePlanRecipe:
    def __init__(self, model: cp_model.CpModel, id: str,
                 produced_item: SparkleItemQty,
                 consumed_items: list[SparkleItemQty],
                 inf: int):
        self.model = model
        self.id = id

        self.produced_item = produced_item
        self.consumed_items = consumed_items
        self.inf = inf

        self.consumed_qty = {
            consumed_item.item: consumed_item.qty
            for consumed_item in self.consumed_items
        }

        self.crafts = self._setup_crafted()
    
    def craft_plan(self, solver: cp_model.CpSolver) -> list[SparklePlanCraftPlan]:
        if solver.Value(self.crafts) == 0:
            return []

        return [SparklePlanCraftPlan(self.id, solver.Value(self.crafts))]

    def _setup_crafted(self):
        crafts_var = self.model.NewIntVar(0, self.inf, f"recipe_crafted_{self.id}")

        return crafts_var
