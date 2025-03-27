from ortools.sat.python import cp_model

from sparkle.types.recipe import SparkleRecipe
from sparkle.plan.types.craft_plan import SparklePlanCraftPlan


class SparklePlanRecipe:
    def __init__(self, model: cp_model.CpModel, inf: int,
                 data: SparkleRecipe):
        self.model = model
        self.inf = inf

        self.data = data

        self.crafts = self._setup_crafts()
    
    def craft_plan(self, solver: cp_model.CpSolver) -> list[SparklePlanCraftPlan]:
        if solver.Value(self.crafts) == 0:
            return []

        return [SparklePlanCraftPlan(self.data.recipe_id, solver.Value(self.crafts))]

    def _setup_crafts(self):
        crafts_var = self.model.NewIntVar(0, self.inf, f"recipe_crafted_{self.data.recipe_id}")

        return crafts_var
