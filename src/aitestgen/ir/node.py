from typing import List 
import ast 

# ====
# Class definition
# ====

class Expression : 
    def __init__ (self): 
        pass 

class Constant (Expression): 
    def __init__ (self, value): 
        self.value = value 
    
    def type (self): 
        return type(self.value) 

class Variable (Expression): 
    def __init__ (self, name :str):
        assert(type(name) is str) 
        self.name = name  
        
class StrVariable (Variable): 
    def __init__(self, name: str):
        super().__init__(name) 

class BinaryExpression (Expression): 
    def __init__ (self, opt :ast.operator, lhs :Expression, rhs :Expression): 
        assert(isinstance(opt, ast.operator))
        assert(isinstance(lhs, Expression))
        assert(isinstance(rhs, Expression))

        self.opt = opt 
        self.lhs = lhs 
        self.rhs = rhs 

class TestGenerationContext : 
    def __init__(self) -> None:
        self.variables = [] 
        self.conditions = [] 

    def add_variable (self, var :Variable): 
        assert(isinstance(var, StrVariable)), 'Error: currently, we only support string-variables' 
        assert(all([var.name != v.name for v in self.variables])), 'Error: duplicated variable name: {}'.format(var.name)
        self.variables.append(var) 

    def add_variables (self, vars :List[Variable]): 
        assert(isinstance(vars, List))
        for v in vars: 
            self.add_variable(v) 

    def add_condition (self, cond): 
        self.conditions.append(cond) 

    def add_conditions (self, conds):
        assert(isinstance(conds, List)) 
        for c in conds: 
            self.add_condition(c) 

    def clone (self): 
        # init my clone 
        my_clone = TestGenerationContext() 

        # setup the variables 
        my_clone.add_variables(self.variables) 

        # setup the conditions 
        my_clone.add_conditions(self.conditions)

        # return 
        return my_clone

# ====
# Node generation functions 
# ====
def create_string_variable_from_arg (ast_arg :ast.arg): 
    assert(isinstance(ast_arg, ast.arg)) 
    return StrVariable(ast_arg.arg) 