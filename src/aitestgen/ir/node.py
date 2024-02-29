import re 
from typing import List, Union, Any
import json 

# ====
# Global 
# ====
NEXT_VARIABLE_ID = 0 

# ====
# Some util functions 
# ====
def preproc_generated_natural_language (nl_str :str): 
    nl_str = re.sub(r"\s+", " ", nl_str)
    return nl_str

# ====
# Class definition: Expression
# ====
class Expression : 
    operator :str = None 
    operands :List = None 

    def __init__ (self): 
        pass 

    def to_json (self) -> Any:
        return json.dumps([self.operator] + [opd.to_json() for opd in self.operands])
    
    def __str__(self) -> str:
        return str(self.to_json())
    
    def to_natural_language(self, *args, **kwargs) -> str:
        return "" 

class Constant (Expression): 
    def __init__ (self, value): 
        self.operands = [value] 
    
    @property
    def type (self): 
        return type(self.value)
    
    @property
    def value (self): 
        return self.operands[0]
    
    def to_json(self) -> Any:
        return self.value 
    
    def to_natural_language(self, *args, **kwargs) -> str:
        if (type(self.value) == str): 
            return f'"{self.value}"'
        else: 
            return str(self.value).lower()

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
        
    def __str__(self) -> str:
        return self.operands[0]
        
    def to_json(self) -> Any:
        return [self.operator] + self.operands
        
    def to_natural_language(self, *args, **kwargs) -> str:
        return f"variable {self.operands[0]}"
        
    @classmethod
    def get_tmp_var (cls): 
        return cls("__var")
    
def substr_operator (s :str, i_start :Union[int, None], i_end :Union[int, None]) -> str: 
    if (i_start is None and i_end is None): 
        return s[:]
    elif (i_start is None and i_end is not None): 
        return s[:i_end] 
    elif (i_start is not None and i_end is None): 
        return s[i_start:]
    else: 
        return s[i_start:i_end]
    
def convert_programming_index_to_natural_language_index (programming_index :int): 
    if (programming_index == 0): 
        return "1st"
    elif (programming_index == 1): 
        return "2nd"
    elif (programming_index == 2): 
        return "3rd"
    else:
        return f"{programming_index+1}th"

class StringOperation (Expression): 
    operators = {
        "subStr":substr_operator, 
        "startsWith": lambda opd_x, opd_y: opd_x.starswith(opd_y), 
        "endsWith": lambda opd_x, opd_y: opd_x.endswith(opd_y)
    }

    def __init__(self, opt :str, opds :List[Expression]):
        assert(opt in StringOperation.operators) 

        self.operator = opt 
        self.operands = opds[:]

        assert(self.operator != "subStr" or len(self.operands) == 3)
        assert(self.operator != "startsWith" or len(self.operands) == 2)
        assert(self.operator != "endsWith" or len(self.operands) == 2)

    def to_natural_language(self, *args, **kwargs) -> str:
        negator = "" 
        if ("negated" in kwargs and kwargs["negated"]): 
            negator = "does not"

        if (self.operator == "subStr"): 
            nl_str = f"the sub-string of {self.operands[0].to_natural_language()}" 
            if (self.operands[1] is not None): # starting index is given 
                i_start = convert_programming_index_to_natural_language_index(self.operands[1])
                nl_str = f"{nl_str} starting from the {i_start} character"
            if (self.operands[2] is not None): # ending index is given 
                i_end = convert_programming_index_to_natural_language_index(self.operands[2]) 
                nl_str = f"{nl_str} ending before the {i_end} character"

        elif (self.operator == "startsWith"): 
            nl_str = f"{self.operands[0].to_natural_language()} {negator} starts with {self.operands[1].to_natural_language()}"

        elif (self.operands == "endsWith"): 
            nl_str = f"{self.operands[0].to_natural_language()} {negator} ends with {self.operands[1].to_natural_language()}"

        else:
            assert(False)

        return preproc_generated_natural_language(nl_str)

class UnaryExpression (Expression): 
    operators = {
        "not": lambda opd: (not opd)
    }

    def __init__(self, opt :str, opd :Expression):
        assert(opt in UnaryExpression.operators)
        assert(isinstance(opd, Expression))

        self.operator = opt 
        self.operands = [opd]

    def to_natural_language(self, *args, **kwargs) -> str:
        if (self.operator == "not"): 
            return f"not {self.operands[0].to_natural_language(negated=True)}" 

        else: 
            assert(False)

class BinaryExpression (Expression): 
    operators = {
        "==": lambda lhs, rhs: (lhs == rhs)
    }

    def __init__ (self, opt :str, lhs :Expression, rhs :Expression): 
        assert(opt in BinaryExpression.operators) 
        assert(isinstance(lhs, Expression))
        assert(isinstance(rhs, Expression))

        self.operator = opt 
        self.operands = [lhs, rhs]

        assert(self.operator != "==" or len(self.operands) == 2)

    def to_natural_language(self, *args, **kwargs) -> str:
        if (self.operator == "=="): 
            return f"{self.operands[0].to_natural_language()} is the same as {self.operands[1].to_natural_language()}"

        else: 
            assert(False)
    
# ====
# Class definition: Statement
# ==== 
class Statement: 
    keyword :str = None
    body :List = None

    def __init__ (self): 
        pass 

    def to_json (self) -> Any:
        return json.dumps([self.keyword] + [content.to_json() for content in self.body])

    def __str__(self) -> str:
        return str(self.to_json())
    
    def to_natural_language(self, *args, **kwargs) -> str:
        return "" 

class AssignStatement (Statement): 
    keyword = ":=" 

    def __init__(self, var :Variable, expr :Expression):
        assert(isinstance(var, Variable))
        assert(isinstance(expr, Expression))

        self.variable = var 
        self.expression = expr
        self.body = [self.expression]

    def to_natural_language(self, *args, **kwargs) -> str:
        return f"{self.variable.to_natural_language()} is {self.expression.to_natural_language()}"
    
class AssertStatement (Statement): 
    keyword = "assert" 

    def __init__(self, bool_expr :Expression):
        assert(isinstance(bool_expr, Expression))
        self.bool_expression = bool_expr

    def to_natural_language(self, *args, **kwargs) -> str:
        return self.bool_expression.to_natural_language() 
    