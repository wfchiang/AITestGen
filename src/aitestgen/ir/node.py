from typing import List, Union, Any
import ast 

# ====
# Global 
# ====
NEXT_VARIABLE_ID = 0 

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
    
    def __str__ (self): 
        if (self.type() is str): 
            return '"{}"'.format(self.value)
        else: 
            return str(self.value)

class UnknownConstant (Constant): # a special constant which denotes "unknown" 
    def __init__(self):
        super().__init__(None) 
    
    def __str__ (self): 
        return '(Unknown)'

class Variable (Expression): 
    def __init__ (self, name :str):
        global NEXT_VARIABLE_ID 

        assert(type(name) is str) 
        
        self.id = NEXT_VARIABLE_ID 
        NEXT_VARIABLE_ID += 1
        
        self.name = name 

    def __hash__ (self): 
        return int(self.id)

    def __eq__ (self, __other): 
        if (isinstance(__other, Variable)): 
            return self.name == __other.name and self.id == __other.id 
        else: 
            return False 
        
    def __str__ (self): 
        return f'###{self.name}_{self.id}###'
        
class StrVariable (Variable): 
    def __init__(self, name: str):
        super().__init__(name) 

class UnaryExpression (Expression): 
    def __init__(self, opt :ast.operator, operand :Expression): 
        assert(isinstance(opt, ast.unaryop)), 'Invalid opt for UnaryExpression: {}'.format(opt)
        assert(isinstance(operand, Expression))
        
        self.opt = opt 
        self.operand = operand 

    def __str__ (self): 
        return '({}, {})'.format(
            str(self.opt.__class__.__name__), 
            str(self.operand)
        )

class BinaryExpression (Expression): 
    def __init__ (self, opt :ast.operator, lhs :Expression, rhs :Expression): 
        assert(isinstance(opt, ast.operator) or isinstance(opt, ast.cmpop)), 'Invalid opt for BinaryExpression: {}'.format(opt)
        assert(isinstance(lhs, Expression))
        assert(isinstance(rhs, Expression))

        self.opt = opt 
        self.lhs = lhs 
        self.rhs = rhs 

    def __str__ (self): 
        return '({}, {}, {})'.format(
            str(self.opt.__class__.__name__), 
            str(self.lhs), 
            str(self.rhs)
        )
    
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
# Node generation functions 
# ====
def create_variable_from_name (var :Union[str, ast.Name]): 
    assert(type(var) is str or isinstance(var, ast.Name))
    return Variable(name=(var if (type(var) is str) else var.id))

def create_variable_from_arg (ast_arg :ast.arg): 
    assert(isinstance(ast_arg, ast.arg)) 
    return Variable(ast_arg.arg) 

def create_temp_variable (): 
    return Variable(f'__tmp_') # "NEXT_VARIABLE_ID" will be bumpped up by 1 by the constructor of class Variable

def negate_expression (expr :Expression): 
    assert(isinstance(expr, Expression)) 

    if (isinstance(expr, UnaryExpression) and isinstance(expr.opt, ast.Not)):
        return expr.operand 
    else: 
        return UnaryExpression(opt=ast.Not(), operand=expr) 
    
# ====
# Some util functions 
# ====
# Given an Expression, count the number of variables as "leaf" in the Expression 
def count_num_leaf_variables (expr :Expression): 
    if (isinstance(expr, Constant)): 
        return 0 
    elif (isinstance(expr, Variable)): 
        return 1 
    elif (isinstance(expr, UnaryExpression)): 
        return count_num_leaf_variables(expr.operand) 
    elif (isinstance(expr, BinaryExpression)): 
        return count_num_leaf_variables(expr.lhs) + count_num_leaf_variables(expr.rhs) 
    else: 
        assert(False), 'Invalid type of expression for count_num_leaf_variables: {}'.format(expr) 