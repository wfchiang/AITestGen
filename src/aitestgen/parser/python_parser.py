import ast, inspect
from typing import List 
from functools import wraps 

from ..ir import node as ir_node 

# ====
# Decorator 
# ====
def analyze (): 
    def _analyze_wrapper (f): 
        # Analyze function "f" 
        print("Analyzing function {}".format(f)) 

        f_ast_node = ast.parse(inspect.getsource(f)) 
        tg_contexts = parse_ast_node_for_test_generation_contexts(f_ast_node)

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
def parse_ast_statement_for_test_generation_conditions (ast_node): 
    return [] 

def parse_ast_node_for_test_generation_contexts (ast_node): 
    if (isinstance(ast_node, ast.Module)): 
        module_body = ast_node.body 
        
        if (len(module_body) == 1): 
            return parse_ast_node_for_test_generation_contexts(module_body[0])

        else: 
            raise UnhandledScenarioException("Can only handle the case of function-def -- the first and the only one under the Module object")
        
    elif (isinstance(ast_node, ast.FunctionDef)): 
        # Grab the function arguments 
        func_args = list(map(lambda arg: ir_node.create_string_variable_from_arg(arg), ast_node.args.args)) 

        # Create a test-generation context 
        tg_context = ir_node.TestGenerationContext() 
        tg_context.add_variables(func_args) 

        test_generation_contexts = [tg_context] 
        
        # Loop through the function body to generate conditions 
        for f_body_stmt in ast_node.body: 
            conds = parse_ast_statement_for_test_generation_conditions(f_body_stmt) 
            assert(isinstance(conds, List)) 

            if (len(conds) == 0): 
                pass 

            elif (len(conds) == 1): 
                test_generation_contexts[-1].add_condition(conds[0])

            elif (len(conds) == 2): 
                tg_contexts_0 = [tgc.clone() for tgc in test_generation_contexts]
                tg_contexts_1 = [tgc.clone() for tgc in test_generation_contexts] 

                for tgc in tg_contexts_0: 
                    tgc.add_condition(conds[0])
                
                for tgc in tg_contexts_1: 
                    tgc.add_condition(conds[1]) 

                test_generation_contexts = tg_contexts_0 + tg_contexts_1

            else: 
                raise UnhandledScenarioException("A statement should generate at most 2 conditions...")

        print(func_args)

    else: 
        raise UnhandledScenarioException("Unhandled AST node type: {} : {}".format(type(ast_node), ast.dump(ast_node, indent=4)))