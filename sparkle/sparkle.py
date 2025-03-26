from ortools.sat.python import cp_model
from collections import defaultdict

class SparklePlan:
    def __init__(self, items, recipes, target_item, target_quantity, inf=1000000000):
        self.model = cp_model.CpModel()

        self.items = items
        self.recipes = recipes
        self.target_item = target_item
        self.target_quantity = target_quantity
        self.inf = inf

        self.recipes_consumed = self._setup_recipes()

        self.op_buy = self._setup_buy()
        self.op_craft = self._setup_craft()
        self.op_craft_produced = self._setup_craft_produced()
        self.op_craft_consumed = self._setup_craft_consumed()
        
        self._setup_balance()
        self._setup_target(target_item, target_quantity)

        self.res_total_cost = self._setup_total_cost()
        self.res_total_buys = self._setup_total_buys()
        self.res_total_crafts = self._setup_total_crafts()

    def solve(self):
        self.model.Minimize(self.res_total_cost)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            min_cost_val = solver.Value(self.res_total_cost)

            buy_plan = [
                (item, i, solver.Value(var))
                for (item, i), var in self.op_buy.items() if solver.Value(var) > 0
            ]

            craft_plan = [
                (item, r_id, solver.Value(var))
                for (item, r_id), var in self.op_craft.items() if solver.Value(var) > 0
            ]

            remaining_quantities = {
                item: solver.Value(
                    self._get_total_bought(item) + self._get_total_crafted(item)
                    - (self._get_total_used(item) + (self.target_quantity if item == self.target_item else 0))
                )
                for item in self.items
            }

            leftovers = {
                item: qty
                for item, qty in remaining_quantities.items() if qty > 0
            }

            return min_cost_val, buy_plan, craft_plan, leftovers
        else:
            return None, None, None, None

    def _setup_recipes(self):
        consumed = defaultdict(list)

        for produced_item, produced_item_recipes in self.recipes.items():
            for r_id, recipe in enumerate(produced_item_recipes):
                for consumed_item in recipe["input"]:
                    if consumed_item not in self.items:
                        raise ValueError(f"Recipe for {produced_item} requires {consumed_item} which is not defined in items")

                    consumed[consumed_item].append((produced_item, r_id))
        
        return consumed

    def _setup_buy(self):
        buy_vars = {}

        for item, data in self.items.items():
            for i, (qty, _) in enumerate(data["supply"]):
                buy_vars[(item, i)] = self.model.NewIntVar(
                    0, self._parse_qty(qty), f"buy_{item}_{i}")
        
        return buy_vars
    
    def _setup_craft(self):
        craft_vars = {}

        for item, item_recipes in self.recipes.items():
            for r_id, _ in enumerate(item_recipes):
                craft_vars[(item, r_id)] = self.model.NewIntVar(
                    0, self.inf, f"craft_{item}_{r_id}")
        
        return craft_vars
    
    def _setup_craft_produced(self):
        return {item: self._setup_craft_produced_item(self.op_craft, item) for item in self.items}
    
    def _setup_craft_consumed(self):
        return {item: self._setup_craft_consumed_item(self.op_craft, item) for item in self.items}

    def _setup_balance(self):
        for item in self.items:
            self._setup_balance_item(item, 0)
    
    def _setup_target(self, item, qty):
        self._setup_balance_item(item, qty)

    def _setup_total_cost(self):
        cost_expr = [
            buy_var * self._get_buy_price(item, i) 
            for (item, i), buy_var in self.op_buy.items()
        ]

        cost_var = self.model.NewIntVar(0, self.inf, "total_cost")

        self.model.Add(cost_var == sum(cost_expr))

        return cost_var

    def _setup_total_buys(self):
        buys_var = self.model.NewIntVar(0, self.inf, "total_buys")

        self.model.Add(buys_var == sum(self.op_buy.values()))
        
        return buys_var

    def _setup_total_crafts(self):
        crafts_var = self.model.NewIntVar(0, self.inf, "total_crafts")

        self.model.Add(crafts_var == sum(self.op_craft.values()))
        
        return crafts_var

    def _setup_craft_produced_item(self, craft_vars, item):
        produced_expr = [
            craft_vars[(item, r_id)] * item_recipe["quantity"]
            for r_id, item_recipe in enumerate(self.recipes.get(item, []))
        ]

        produced_var = self.model.NewIntVar(0, self.inf, f"produced_{item}")

        self.model.Add(produced_var == sum(produced_expr))

        return produced_var
    
    def _setup_craft_consumed_item(self, craft_vars, item):
        consumed_expr = [
            craft_vars[(prod_item, r_id)] * self.recipes[prod_item][r_id]["input"][item]
            for prod_item, r_id in self.recipes_consumed.get(item, [])
        ]

        consumed_var = self.model.NewIntVar(0, self.inf, f"consumed_{item}")

        self.model.Add(consumed_var == sum(consumed_expr))

        return consumed_var
    
    def _setup_balance_item(self, item, min_qty):
        total_in = self._get_total_bought(item) + self._get_total_crafted(item)
        total_out = self._get_total_used(item)

        self.model.Add(total_in - total_out >= min_qty)

    def _parse_qty(self, qty):
        return self.inf if qty == -1 else qty
    
    def _get_buy_price(self, item, i):
        return self.items[item]["supply"][i][1]
    
    def _get_sell_price(self, item, i):
        return self.items[item]["demand"][i][1]
    
    def _get_total_bought(self, item):
        return sum(self.op_buy[(item, i)] for i in range(len(self.items[item]["supply"])))
    
    def _get_total_crafted(self, item):
        return self.op_craft_produced[item]
    
    def _get_total_used(self, item):
        return self.op_craft_consumed[item]
