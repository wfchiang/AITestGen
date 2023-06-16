from typing import List 
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

class UnknownConstant (Constant): # a special constant which denotes "unknown" 
    def __init__(self):
        super().__init__(None)

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
            return self.name == __other.name 
        else: 
            return False 
        
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

# ====
# Node generation functions 
# ====
def create_string_variable_from_arg (ast_arg :ast.arg): 
    assert(isinstance(ast_arg, ast.arg)) 
    return StrVariable(ast_arg.arg) 

def create_new_temp_string_variable (): 
    return StrVariable(f'__tmp_str_{NEXT_VARIABLE_ID}') # "NEXT_VARIABLE_ID" will be bumpped up by 1 by the constructor of class Variable