from typing import List, Union, Any
import json 

# ====
# Global 
# ====
NEXT_VARIABLE_ID = 0 

# ====
# Class definition
# ====
class Expression : 
    operator :str = None 
    operands :List = None 

    def __init__ (self): 
        pass 

    def as_json (self) -> List:
        return json.dumps([self.operator] + [opd.as_json() for opd in self.operands])

class Constant (Expression): 
    def __init__ (self, value): 
        self.operands = [value] 
    
    def type (self): 
        return type(self.value)
    
    @property
    def value (self): 
        return self.operands[0]
    
    def as_json(self) -> List:
        return self.value 

class Variable (Expression): 
    operator :str = "var"

    def __init__ (self, name :str):
        global NEXT_VARIABLE_ID 

        assert(type(name) is str) 
        
        self.id = NEXT_VARIABLE_ID 
        NEXT_VARIABLE_ID += 1
        
        self.name = name 
        self.operands = [f"{self.name}_{self.id}"]

    def __hash__ (self): 
        return int(self.id)

    def __eq__ (self, __other): 
        if (isinstance(__other, Variable)): 
            return self.name == __other.name and self.id == __other.id 
        else: 
            return False 
        
    @classmethod
    def get_tmp_var (cls): 
        return cls("__var")

class StringOperation (Expression): 
    operators = [
        "subStr", 
        "startsWith", 
        "endsWith",
    ] 

    def __init__(self, opt :str, opds :List):
        assert(opt in StringOperation.operators) 

        self.operator = opt 
        self.operands = opds[:]

class UnaryExpression (Expression): 
    operators = [
        "not"
    ]

    def __init__(self, opt :str, opds :List):
        assert(opt in UnaryExpression.operators)
        assert(len(opds) == 1)

        self.operator = opt 
        self.operands = opds[:]

class BinaryExpression (Expression): 
    operators = [
        "=="
    ]

    def __init__ (self, opt :str, opds :List): 
        assert(opt in BinaryExpression.operators)
        assert(len(opds) == 2) 

        self.operator = opt 
        self.operands = opds[:]
    
# ====
# Solution: a map of Variable to Constant 
# ====
class Solution: 
    def __init__(self) -> None:
        self.assignments = {} 
    
    def add (self, var :Variable, val :Any): 
        assert(isinstance(var, Variable))
        if (not isinstance(val, Constant)): 
            val = Constant(val) 

        self.assignments[var] = val 

    def __dict__ (self): 
        to_dict = {} 
        for var, val in self.assignments.items(): 
            to_dict[str(var)] = val.value 
        return to_dict 
    
    def clone (self): 
        another_me = Solution() 
        for var, val in self.assignments.items(): 
            another_me.add(var, val) 
        return another_me
    
# ====
# Some util functions 
# ====
# Given an Expression, count the number of variables as "leaf" in the Expression 
def count_num_leaf_variables (expr :Expression): 
    if (isinstance(expr, Constant)): 
        return 0 
    elif (isinstance(expr, Variable)): 
        return 1 
    else: 
        leaves = 0 
        for opd in expr.operands: 
            leaves += count_num_leaf_variables(opd) 
        return leaves