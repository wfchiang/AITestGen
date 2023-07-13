import ast 
from typing import Union 
import logging 
import traceback 

from . import node as ir_node 

# ====
# Globals 
# ====
logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO) 

MAX_BRANCH_DEPTH = 3

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

    def add_to_store (self, var :Union[ast.Name, ir_node.Variable], val :ir_node.Expression): 
        # check parameters 
        var = (var if (not isinstance(var, ast.Name)) else ir_node.create_variable_from_name(var))
        assert(isinstance(var, ir_node.Variable)), 'Invalid variable type: {}'.format(type(var))
        assert(var not in self.store), 'ERROR: variable {} is not new to the ExecutionContext'.format(str(var))

        assert(isinstance(val, ir_node.Expression)), 'Invalid value type: {}'.format(type(val))

        self.store[var] = val
    
    def query_store_for_latest_var_by_name (self, var_name :str): 
        assert(type(var_name) is str) 

        var = None 
        latest_id = None 
        for k,v in self.store.items(): 
            if (k.name == var_name): 
                if (latest_id is None or latest_id < k.id): 
                    latest_id = k.id 
                    var = k 

        return var 

    def read_store_by_name (self, var_name :str): 
        assert(type(var_name) is str) 

        val = None 
        latest_id = None 
        for k,v in self.store.items(): 
            if (k.name == var_name): 
                if (latest_id is None or latest_id < k.id): 
                    latest_id = k.id 
                    val = v 

        return val 

    def __dict__ (self): 
        # dump the store 
        store = {} 
        for k,v in self.store.items(): 
            k = str(k) 
            v = str(v)
            if (k in store): 
                logger.error('[ERROR] duplicated str(k) in store: {}'.format(k))
            store[k] = v 
                
        # return 
        return {
            "store": store, 
            "next_statement": (None if (len(self.statements) == 0) else ast.dump(self.statements[0], indent=4)), 
            "num_statements": len(self.statements), 
            "branch_depth": self.branch_depth, 
            "conditions": [str(c) for c in self.conditions]
        }

class Executor : 
    def __init__ (self, max_branch_depth :int=3): 
        self.max_branch_depth = max_branch_depth

    # Execute one statement from the context 
    # It takes an initial context, and generates the "next-stage" context(s) 
    # Note that some statement may create 2 "next-stage" contexts 
    # So, this "step" function will return 2 next-stage contexts: true-br and false-br 
    # If there is only one context returned, false-br will be None 
    def step (self, exe_context :ExecutionContext): 
        assert(isinstance(exe_context, ExecutionContext)) 

        if (len(exe_context.statements) == 0): # no statement to execute 
            return None 

        else: 
            # clone the context and pop for the statement 
            true_br_context = exe_context.clone()
            false_br_context = None 

            curr_statement = true_br_context.statements[0] 
            true_br_context.statements = true_br_context.statements[1:] 

            # execute the statement 
            try: 
                if (isinstance(curr_statement, ast.Assign)): 
                    targets = curr_statement.targets
                    
                    if (len(targets) > 1): 
                        logger.error('[WARNING] multi assignment target ({}) is not supported...'.format(len(targets)))
                        logger.error(ast.dump(curr_statement, indent=4))

                    else: 
                        target = targets[0] 
                        assert(isinstance(target, ast.Name)), '[WARNING] only support target as Name for Assign...' 
                        source = self.eval(expr=curr_statement.value, exe_context=true_br_context) 
                        true_br_context.add_to_store(var=target, val=source) 
                        
                elif (isinstance(curr_statement, ast.Assert)): 
                    test_expr = self.eval(curr_statement.test, exe_context=true_br_context) 
                    true_br_context.branch_depth = true_br_context.branch_depth + 1 
                    
                    if (true_br_context.branch_depth <= MAX_BRANCH_DEPTH): 
                        false_br_context = true_br_context.clone() 
                        false_br_context.conditions.append(ir_node.negate_expression(test_expr))
                    
                    true_br_context.conditions.append(test_expr) 

                else: 
                    logger.error('[WARNING] unsupported statement -- skipping and relaxing the constraint')
                    logger.info(ast.dump(curr_statement, indent=4))
                    pass 

            except:  
                traceback.print_exc() 
                logger.error('Stepping failed... Ignore the above error and continue...') 

            # return 
            return true_br_context, false_br_context 

    # Evaluate the ast node. 
    # It should return an ir_node.Expression 
    # For any unhandled evaluation scenario, we will just return ir_node.UnknownConstant() 
    def eval (self, expr :ast.AST, exe_context :ExecutionContext): 
        assert(isinstance(expr, ast.AST))
        assert(isinstance(exe_context, ExecutionContext))

        eval_result = ir_node.UnknownConstant()  

        try: 
            if (isinstance(expr, ast.Constant)): 
                eval_result = ir_node.Constant(expr.value) 
            
            elif (isinstance(expr, ast.Name)): 
                eval_result = exe_context.query_store_for_latest_var_by_name(expr.id)

            elif (isinstance(expr, ast.UnaryOp)): 
                eval_result = ir_node.UnaryExpression(
                    opt=expr.op, 
                    operand=self.eval(expr.operand, exe_context)
                )

            elif (isinstance(expr, ast.BinOp)): 
                eval_result = ir_node.BinaryExpression(
                    opt=expr.op, 
                    lhs=self.eval(expr.left, exe_context), 
                    rhs=self.eval(expr.right, exe_context) 
                )
            
            elif (isinstance(expr, ast.Compare)): 
                assert(len(expr.ops) == 1), 'Only support ast.Compare with 1 ops for now...'
                assert(len(expr.comparators) == 1), 'Only support ast.Compare with 1 comparators for now...' 

                op = expr.ops[0] 
                lhs = self.eval(expr.left, exe_context) 
                rhs = self.eval(expr.comparators[0], exe_context) 

                eval_result = ir_node.BinaryExpression(
                    opt=op, 
                    lhs=lhs, 
                    rhs=rhs 
                )

            else: 
                logger.error('Not supportted expression to eval: {}'.format(ast.dump(expr, indent=4)))

        except: 
            traceback.print_exc() 
            logger.error('Evaluation failed... Ignore the above error and continue...')
        
        # return 
        return eval_result
