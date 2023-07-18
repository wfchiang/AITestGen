import ast, inspect
import json 
from typing import List 
from functools import wraps 
import logging 

from ..ir import node as ir_node 
from ..ir import symbolic_executor as ir_se
from ..ir import solver as ir_solver 

# ====
# Globals 
# ====
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ====
# Decorator 
# ====
def analyze (): 
    def _analyze_wrapper (f): 
        # Analyze function "f" 
        logger.info("Analyzing function {}".format(f)) 

        # Extract the function source code 
        function_source_code = inspect.getsource(f)

        # Create the initial context 
        init_exe_context = parse_source_code_to_symbolic_execution_context(function_source_code)
        
        # Solve for the test cases 
        context_solution_list = ir_solver.solve_for_test_cases(init_exe_context)

        # Wrap the original function "f" and return 
        @wraps(f) 
        def _f_wrapper (*args, **kwargs): 
            return f(*args, **kwargs) 

        return _f_wrapper 
    
    return _analyze_wrapper 

# ====
# Exceptions (and handlers)
# ====
class UnhandledScenarioException (Exception): 
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# ====
# Parser procedure
# ====
def parse_ast_node_to_symbolic_execution_context (ast_node): 
    if (isinstance(ast_node, ast.Module)): 
        module_body = ast_node.body 
        
        if (len(module_body) == 1): 
            return parse_ast_node_to_symbolic_execution_context(module_body[0])

        else: 
            raise UnhandledScenarioException("Can only handle the case of function-def -- the first and the only one under the Module object")
        
    elif (isinstance(ast_node, ast.FunctionDef)): 
        # Grab the function arguments 
        func_args = list(map(lambda arg: ir_node.create_variable_from_arg(arg), ast_node.args.args)) 

        # Create a symbolic execution context 
        se_context = ir_se.ExecutionContext() 
        for f_arg in func_args: 
            se_context.add_to_store(f_arg, ir_node.UnknownConstant()) 

        # Grab the statements 
        for statement in ast_node.body: 
            se_context.statements.append(statement) 

        # Return 
        return se_context

    else: 
        raise UnhandledScenarioException("Unhandled AST node type: {} : {}".format(type(ast_node), ast.dump(ast_node, indent=4))) 
    
def parse_source_code_to_symbolic_execution_context (code :str): 
    assert(type(code) is str) 

    ast_node = ast.parse(code) 
    return parse_ast_node_to_symbolic_execution_context(ast_node) 
