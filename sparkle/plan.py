import itertools
from ortools.sat.python import cp_model

from sparkle.plan_item import SparklePlanItem
from sparkle.plan_itemqty import SparklePlanItemQty
from sparkle.plan_recipe import SparklePlanRecipe

# TODO: Reverse topological pruning to remove unused items

class SparklePlan:
    def __init__(self, items: dict, recipes, target_item: SparklePlanItemQty, inf=int(1e10)):
        self.model = cp_model.CpModel()

        self.items = items
        self.recipes = recipes
        self.target_item = target_item
        self.inf = inf

        self.recipe_vars = {
            recipe_id: SparklePlanRecipe(
                self.model, recipe_id, 
                recipe["produced_item"], recipe["consumed_items"],
                inf
            )
            for recipe_id, recipe in enumerate(recipes)
        }

        self.item_vars = {
            item_id: SparklePlanItem(
                self.model, item_id, 
                item["demand"], item["supply"],
                [r for r in self.recipe_vars.values() if r.produced_item.item == item_id],
                [r for r in self.recipe_vars.values() if item_id in r.consumed_qty],
                inf
            )
            for item_id, item in items.items()
        }

        self._setup_target()

        self.total_cost = self._setup_total_cost()
        self.total_buys = self._setup_total_buys()
        self.total_crafts = self._setup_total_crafts()

    def solve(self):
        self.model.Minimize(self.total_cost)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            min_cost_val = solver.Value(self.total_cost)

            buy_plan = itertools.chain.from_iterable(
                item_var.buy_plan(solver) for item_var in self.item_vars.values()
            )

            craft_plan = [recipe_var.craft_plan(solver) for recipe_var in self.recipe_vars.values()]
            craft_plan = [(self.recipe_vars[r[0]], r[1]) for r in craft_plan if r is not None]

            remaining_quantities = {
                item: solver.Value(
                    item_var.bought + item_var.produced 
                    - (item_var.consumed + (self.target_item.qty if item == self.target_item.item else 0))
                )
                for item, item_var in self.item_vars.items()
            }

            leftovers = {
                item: qty
                for item, qty in remaining_quantities.items() if qty > 0
            }

            return min_cost_val, buy_plan, craft_plan, leftovers
        else:
            return None, None, None, None
    
    def _setup_target(self):
        self.item_vars[self.target_item.item] = self.target_item.qty

    def _setup_total_cost(self):
        cost_expr = [item_var.cost for item_var in self.item_vars.values()]
        cost_var = self.model.NewIntVar(0, self.inf, "total_cost")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_total_buys(self):
        buys_expr = [item_var.bought for item_var in self.item_vars.values()]
        buys_var = self.model.NewIntVar(0, self.inf, "total_buys")

        self.model.Add(buys_var == sum(buys_expr))
        
        return buys_var

    def _setup_total_crafts(self):
        crafts_expr = [recipe_var.crafts for recipe_var in self.recipe_vars.values()]
        crafts_var = self.model.NewIntVar(0, self.inf, "total_crafts")

        self.model.Add(crafts_var == sum(crafts_expr))
        
        return crafts_var