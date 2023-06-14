class Operator : 
    def __init__ (self, name :str):
        assert(type(name) is str) 
        self.name = name  
        
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
    def __init__ (self, opt :Operator, lhs :Expression, rhs :Expression): 
        assert(isinstance(opt, Operator))
        assert(isinstance(lhs, Expression))
        assert(isinstance(rhs, Expression))

        self.opt = opt 
        self.lhs = lhs 
        self.rhs = rhs 

