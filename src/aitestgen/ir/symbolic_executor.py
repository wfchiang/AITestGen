import ast 

from . import node as ir_node 

# ====
# Globals 
# ====

# ====
# Class definition(s) 
# ====
class ExecutionContext : 
    def __init__ (self): 
        self.store = {} 
        self.conditions = [] 
        self.statements = []

        self.branch_depth = 0

    def clone (self): 
        my_clone = ExecutionContext() 

        # clone the store 
        for k, v in self.store.items(): 
            my_clone.store[k] = v 

        # clone the conditions 
        my_clone.conditions = [c for c in self.conditions]

        # clone the statements 
        my_clone.statements = [s for s in self.statements]

        # return 
        return my_clone

    def add_to_store (self, var :ir_node.Variable, val :ir_node.Expression): 
        assert(isinstance(var, ir_node.Variable)), 'Invalid variable type: {}'.format(type(var))
        assert(isinstance(val, ir_node.Expression)), 'Invalid value type: {}'.format(type(val))

        assert(var not in self.store), 'ERROR: variable {} is not new to the ExecutionContext'.format(var.name)

        self.store[var] = val

class Executor : 
    def __init__ (self, max_branch_depth :int=3): 
        self.max_branch_depth = max_branch_depth

    def step (self, exe_context :ExecutionContext): 
        assert(isinstance(exe_context, ExecutionContext)) 

        if (len(exe_context.statements) == 0): # no statement to execute 
            return None 

        else: 
            # clone the context and pop for the statement 
            next_exe_context = exe_context.clone()

            curr_statement = next_exe_context.statements[0] 
            next_exe_context.statements = next_exe_context.statements[1:] 

            # execute the statement 
            if (isinstance(curr_statement, ast.Assert)): 
                pass 

            else: 
                print('[WARNING] unsupported statement -- skipping and relaxing the constraint')
                print(ast.dump(curr_statement, indent=4))
                pass 

            # return 
            return next_exe_context 


