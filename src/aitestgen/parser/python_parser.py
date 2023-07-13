import ast, inspect
import json 
from typing import List 
from functools import wraps 
import logging 

from ..ir import node as ir_node, symbolic_executor as ir_se 
from . import ir_2_llm_prompt 

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

        # init the symbolic execution context 
        f_ast_node = ast.parse(inspect.getsource(f)) 
        init_se_context = parse_ast_node_to_symbolic_execution_context(f_ast_node) 

        # DEBUG 
        logger.info(json.dumps(init_se_context.__dict__(), indent=4))

        # go for the symbolic execution 
        se_executor = ir_se.Executor() 

        next_se_contexts = [init_se_context] 
        final_se_contexts = [] 
        while (len(next_se_contexts) > 0): 
            # pop one symbolic execution context 
            next_se_context = next_se_contexts[0]
            next_se_contexts = next_se_contexts[1:]

            # DEBUG 
            logger.info(json.dumps(next_se_context.__dict__(), indent=4)) 

            # Go for a step for the context 
            if (len(next_se_context.statements) == 0): # if there is no more statement to execute, add it to the final contexts 
                final_se_contexts.append(next_se_context) 
            
            else: 
                true_br_context, false_br_context = se_executor.step(next_se_context)
                assert(true_br_context is not None) 
                next_se_contexts.append(true_br_context) 
                if (false_br_context is not None): 
                    next_se_contexts.append(false_br_context)

        # DEBUG 
        ir_2_llm_prompt.generate_prompt_from_execution_context(final_se_contexts[1])

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