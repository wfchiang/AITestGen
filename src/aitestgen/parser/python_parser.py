import ast, inspect
from functools import wraps 

# ====
# Decorator 
# ====
def analyze (): 
    def _analyze_wrapper (f): 
        # Analyze function "f" 
        print("Analyzing function {}".format(f)) 

        f_ast_node = ast.parse(inspect.getsource(f)) 
        parse_ast_node(f_ast_node)

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
def parse_ast_node (ast_node): 
    if (isinstance(ast_node, ast.Module)): 
        module_body = ast_node.body 
        
        if (len(module_body) == 1): 
            return parse_ast_node(module_body[0])

        else: 
            raise UnhandledScenarioException("Can only handle the case of function-def -- the first and the only one under the Module object")
        
    elif (isinstance(ast_node, ast.FunctionDef)): 
        pass 

    else: 
        raise UnhandledScenarioException("Unhandled AST node type: {} : {}".format(type(ast_node), ast.dump(ast_node, indent=4)))