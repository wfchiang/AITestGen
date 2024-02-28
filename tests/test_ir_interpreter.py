from aitestgen.ir import node as ir_node 
from aitestgen.ir.interpreter import ExecutionContext
from aitestgen.ir.interpreter import interpret_json_expression, interpret_json_statement 

import logging 
logging.basicConfig(level=logging.INFO)

# ====
# Utils
# ====
def get_fresh_exe_context (): 
    ir_node.NEXT_VARIABLE_ID = 0
    return ExecutionContext() 

# ====
# Tests for interpret_json_expression
# ====
def test_interpret_json_expression_0 (): 
    exe_context = get_fresh_exe_context() 

    json_expr = 1 
    expr = interpret_json_expression(json_obj=json_expr, exe_context=exe_context) 
    assert(isinstance(expr, ir_node.Constant))
    assert(expr.type is int)
    assert(expr.value == 1)

    json_expr = "abc"
    expr = interpret_json_expression(json_obj=json_expr, exe_context=exe_context)
    assert(isinstance(expr, ir_node.Constant))
    assert(expr.type is str and expr.value == "abc")

def test_interpret_json_expression_1 (): 
    exe_context = get_fresh_exe_context() 

    json_expr = ["not", True]
    expr = interpret_json_expression(json_obj=json_expr, exe_context=exe_context) 
    assert(isinstance(expr, ir_node.UnaryExpression))
    assert(expr.to_natural_language() == "not true")

def test_interpret_json_expression_2 (): 
    exe_context = get_fresh_exe_context() 

    json_expr = ["startsWith", "xyz", "abc"]
    expr = interpret_json_expression(json_obj=json_expr, exe_context=exe_context) 
    assert(isinstance(expr, ir_node.StringOperation))
    assert(expr.to_natural_language() == '"xyz" starts with "abc"')

def test_interpret_json_expression_3 (): 
    exe_context = get_fresh_exe_context() 

    json_expr = ["==", "xyz", "abc"]
    expr = interpret_json_expression(json_obj=json_expr, exe_context=exe_context) 
    assert(isinstance(expr, ir_node.BinaryExpression))
    assert(expr.to_natural_language() == '"xyz" is the same as "abc"')

def test_interpret_json_expression_4 (): 
    exe_context = get_fresh_exe_context() 
    
    json_expr = ["==", ["var", "xyz"], ["var", "abc"]]
    expr = interpret_json_expression(json_obj=json_expr, exe_context=exe_context) 
    assert(isinstance(expr, ir_node.BinaryExpression))
    assert(expr.to_natural_language() == 'variable xyz_0 is the same as variable abc_1')

# ====
# Tests for interpret_json_statement
# ====
def test_interpret_json_statement_0 (): 
    exe_context = get_fresh_exe_context() 

    json_stat = [":=", ["var", "xyz"], ["var", "abc"]] 
    exe_context = interpret_json_statement(json_obj=json_stat, exe_context=exe_context)
    assert(isinstance(exe_context, ExecutionContext))
    assert(exe_context.executed_statements[-1].to_natural_language() == "variable xyz_0 is variable abc_1")

def test_interpret_json_statement_1 (): 
    exe_context = get_fresh_exe_context()  

    json_stat = [":=", ["var", "xyz"], ["var", "abc"]] 
    exe_context = interpret_json_statement(json_obj=json_stat, exe_context=exe_context)
    assert(isinstance(exe_context, ExecutionContext))
    assert(len(exe_context.unbounded_variables) == 1)
    assert(exe_context.executed_statements[-1].to_natural_language() == "variable xyz_0 is variable abc_1")

    json_stat = [":=", ["var", "pqr"], ["var", "xyz"]]
    exe_context = interpret_json_statement(json_obj=json_stat, exe_context=exe_context)
    assert(isinstance(exe_context, ExecutionContext))
    assert(len(exe_context.unbounded_variables) == 1)
    assert(exe_context.executed_statements[-1].to_natural_language() == "variable pqr_2 is variable xyz_0")

    json_stat = [":=", ["var", "xyz"], ["var", "ijk"]]
    exe_context = interpret_json_statement(json_obj=json_stat, exe_context=exe_context)
    assert(isinstance(exe_context, ExecutionContext))
    assert(len(exe_context.unbounded_variables) == 2)
    assert(exe_context.executed_statements[-1].to_natural_language() == "variable xyz_3 is variable ijk_4")

    json_stat = [":=", ["var", "uvw"], ["var", "pqr"]]
    exe_context = interpret_json_statement(json_obj=json_stat, exe_context=exe_context)
    assert(isinstance(exe_context, ExecutionContext))
    assert(len(exe_context.unbounded_variables) == 2)
    assert(exe_context.executed_statements[-1].to_natural_language() == "variable uvw_5 is variable pqr_2")
