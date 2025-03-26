from ortools.sat.python import cp_model

from sparkle.plan_itemqty import SparklePlanItemQty

class SparklePlanRecipe:
    def __init__(self, model: cp_model.CpModel, id: str,
                 produced_item: SparklePlanItemQty,
                 consumed_items: list[SparklePlanItemQty],
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
    
    def craft_plan(self, solver: cp_model.CpSolver):
        if solver.Value(self.crafts) == 0:
            return None
            
        return (self.id, solver.Value(self.crafts))

    def _setup_crafted(self):
        crafts_var = self.model.NewIntVar(0, self.inf, f"recipe_crafted_{self.id}")

        return crafts_var

'''
        consumed_expr = [
            craft_vars[(prod_item, r_id)] * self.recipes[prod_item][r_id]["input"][item]
            for prod_item, r_id in self.recipes_consumed.get(item, [])
        ]

'''