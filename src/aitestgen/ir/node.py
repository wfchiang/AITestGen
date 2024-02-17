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
# State: a mapping from variable to expression 
# ====
class State: 
    def __init__(self) -> None:
        self.var_2_expr = {}  
    
    def add (self, var :Variable, value :Expression): 
        assert(isinstance(var, Variable))
        assert(isinstance(value, Expression))
        self.var_2_expr[var] = value 

    def to_json (self):
        state_json = {}  
        for var, value in self.var_2_expr.items(): 
            state_json[var.operands[0]] = value.to_json() 
        return state_json
    
    def clone (self): 
        another_me = State()  
        for var, value in self.var_2_expr.items(): 
            another_me.add(var, value) 
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