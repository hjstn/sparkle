from ortools.sat.python import cp_model

class SparklePlanBase:
    def __init__(self, model: cp_model.CpModel, inf: int):
        self.model = model
        self.inf = inf
