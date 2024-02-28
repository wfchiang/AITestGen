from typing import List, Union, Tuple
from .node import Expression
from .node import Constant, Variable
from .node import StringOperation
from .node import UnaryExpression, BinaryExpression
from .node import Statement 
from .node import AssignStatement

import logging
logging.basicConfig(level=logging.INFO)

class ExecutionContext : 
    def __init__ (self): 
        self.store = {} # Variable (Expression) -> Expression
        self.conditions = [] 
        self.executed_statements = []
        self.unbounded_variables = [] 

    def clone (self): 
        my_clone = ExecutionContext() 
        my_clone.store = { k:v for k,v in self.store.items() }
        my_clone.conditions = self.conditions[:]
        my_clone.executed_statements = self.executed_statements[:]
        my_clone.unbounded_variables = self.unbounded_variables[:]
        return my_clone
    
    def read_latest_var (self, var_name :str) -> Tuple[Union[Expression, None], Union[Expression, None]]: 
        latest_var = None 
        latest_expr = None 
        for var, expr in self.store.items(): 
            if (var.name == var_name): 
                if (latest_var is None or latest_var.id < var.id): 
                    latest_var = var 
                    latest_expr = expr 
        return (latest_var, latest_expr) 

# ====
# Interpretation functions
# ====
def interpret_json_expression (
        json_obj :Union[List, str, int, float, bool], 
        exe_context :ExecutionContext
) -> Expression: 
    """
    This function will cause side-effects to exe_context (ExecutionContext)
    1. add unbounded variables
    """
    
    if (isinstance(json_obj, List)): 
        assert(len(json_obj) >= 2) 

        opt = json_obj[0]
        assert(type(opt) is str), f"Invalid type of opt: {type(opt)}" 

        if (opt == Variable.operator):
            var_name = json_obj[1] 
            latest_var, _ = exe_context.read_latest_var(var_name=var_name)
            if (latest_var is None): 
                new_var = Variable(name=var_name)
                exe_context.unbounded_variables.append(new_var)
                return new_var
            else: 
                return latest_var

        elif (opt in StringOperation.operators): 
            opds = [interpret_json_expression(json_obj=json_opd, exe_context=exe_context) for json_opd in json_obj[1:]] 
            return StringOperation(opt=opt, opds=opds)
        
        elif (opt in UnaryExpression.operators): 
            opds = [interpret_json_expression(json_obj=json_opd, exe_context=exe_context) for json_opd in json_obj[1:]] 
            assert(len(opds) == 1)
            return UnaryExpression(opt=opt, opd=opds[0]) 
        
        elif (opt in BinaryExpression.operators):
            opds = [interpret_json_expression(json_obj=json_opd, exe_context=exe_context) for json_opd in json_obj[1:]] 
            assert(len(opds) == 2)
            return BinaryExpression(opt=opt, lhs=opds[0], rhs=opds[1])
    
        else: 
            assert(False), f"Invalid json list: {json_obj}"

    elif (type(json_obj) in [str, int, float, bool]): 
        return Constant(json_obj)
    
    else: 
        assert(False), f"Invalid type of json_obj: {type(json_obj)}"

# ====
# Parser function for Expression 
# ====
def interpret_json_statement (
        json_obj :List, 
        exe_context :ExecutionContext
) -> ExecutionContext: 
    assert(isinstance(json_obj, List)) 
    assert(len(json_obj) > 0)

    next_exe_context = exe_context.clone() 
    stat_keyword = json_obj[0] 
    if (stat_keyword == AssignStatement.keyword): 
        assert(len(json_obj) == 3)

        assert(json_obj[1][0] == Variable.operator)
        var_name = json_obj[1][1] 
        var = Variable(name=var_name)

        expr = interpret_json_expression(json_obj[2], exe_context=next_exe_context)

        next_exe_context.executed_statements.append(AssignStatement(var=var, expr=expr)) 
        next_exe_context.store[var] = expr 

    else: 
        assert(False), f"Unknown statement keyword: {stat_keyword}"

    return next_exe_context