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
            return f"{self.value}"

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
        
    def to_natural_language(self, *args, **kwargs) -> str:
        if (self.var_type is str):
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
            return nl_str

        elif (self.operator == "startsWith"): 
            return f"{self.operands[0].to_natural_language()} {negator} starts with {self.operands[1].to_natural_language()}"

        elif (self.operands == "endsWith"): 
            return f"{self.operands[0].to_natural_language()} {negator} ends with {self.operands[1].to_natural_language()}"

        else:
            assert(False)

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
            return self.operands[0].to_natural_language(negated=True)

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
# Parser function 
# ====
def parse_json_to_expression (json_obj :Union[List, str, int, float, bool]): 
    if (isinstance(json_obj, List)): 
        assert(len(json_obj) >= 2) 

        opt = json_obj[0]
        assert(type(opt) is str), f"Invalid type of opt: {type(opt)}" 

        opds = json_obj[1:] 

        if (opt == Variable.operator):
            assert(len(opds) == 1) 
            return Variable(name=opds[0])

        elif (opt in StringOperation.operators): 
            return StringOperation(opt=opt, opds=opds)
        
        elif (opt in UnaryExpression.operators): 
            assert(len(opds) == 1)
            return UnaryExpression(opt=opt, opd=opds[0]) 
        
        elif (opt in BinaryExpression.operators):
            assert(len(opds) == 2)
            return BinaryExpression(opt=opt, lhs=opds[0], rhs=opds[1])
    
        else: 
            assert(False), f"Invalid json list: {json_obj}"

    elif (type(json_obj) in [str, int, float, bool]): 
        return Constant(json_obj)
    
    else: 
        assert(False), f"Invalid type of json_obj: {type(json_obj)}"
    
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