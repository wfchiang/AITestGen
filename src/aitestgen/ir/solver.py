import ast 
import logging 
from ..ir import node as ir_node 
from ..ir.symbolic_executor import Executor, ExecutionContext
from ..llm.client import ChatGPTClient 

# ====
# Globals 
# ====
logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO) 

MAX_NUM_TRIALS = 3 

# ==== 
# find solutions/test-cases for the unbounded variables 
# Returns a list of context-solution pair: [(context_1, solution_1), (context_2, solution_2), ...]
# Each context is an ExecutionContext 
# Each solution is a map of variable->(str-)value
# ====
def solve_for_test_cases (exe_context :ExecutionContext, max_num_trials :int=MAX_NUM_TRIALS): 
    assert(max_num_trials > 0)

    # symbolically execute the code to explore the final contexts 
    symbolic_executor = Executor() 
    final_contexts = symbolic_executor.execute(exe_context) 

    # solve for the test-cases 
    chatgpt_client = ChatGPTClient() 
    context_solution_list = [] 
    for f_ctx in final_contexts: 
        original_f_ctx = f_ctx.clone()

        for trial in range(0, max_num_trials): 
            # DEBUG 
            # print('==== Context ====')
            # print(f_ctx.__dict__())

            sol = chatgpt_client.solve_context(f_ctx) 

            # validate the solution 
            is_valid_sol = validate_solution(original_f_ctx, sol) 
            
            if (is_valid_sol): 
                # add the Context-Solution pair 
                context_solution_list.append((original_f_ctx, sol)) 

                # DEBUG 
                # print('==== Solution ====')
                # print(sol.__dict__())

                break 

            else: # add more conditions to try again...
                for var, val in sol.assignments.items(): 
                    f_ctx.conditions.append(
                        ir_node.UnaryExpression(
                            ast.Not(), 
                            ir_node.BinaryExpression(ast.Eq(), var, val)
                        )
                    ) 

    # return 
    return context_solution_list 

# ====
# Partially evaluate an Expression with a Solution 
# Return an UnknownConstant if failing to evaluate 
# ====
def eval_expression_partially_with_solution (expr :ir_node.Expression, soln :ir_node.Solution): 
    assert(isinstance(expr, ir_node.Expression))
    assert(isinstance(soln, ir_node.Solution)) 

    if (isinstance(expr, ir_node.Constant)):
        return expr 
    
    elif (isinstance(expr, ir_node.Variable)): 
        if (expr in soln.assignments): 
            return soln.assignments[expr] 
        else: 
            return expr 
    
    elif (isinstance(expr, ir_node.UnaryExpression)): 
        operand = eval_expression_partially_with_solution(expr.operand, soln)

        if (isinstance(operand, ir_node.Constant)): 
            if (isinstance(expr.opt, ast.Not)):           
                if (operand.type() is bool): 
                    return ir_node.Constant((not operand.value))
        
        else: 
            return ir_node.UnaryExpression(expr.opt, operand) 
            
    elif (isinstance(expr, ir_node.BinaryExpression)): 
        lhs = eval_expression_partially_with_solution(expr.lhs, soln) 
        rhs = eval_expression_partially_with_solution(expr.rhs, soln) 

        if (isinstance(lhs, ir_node.Constant) and isinstance(rhs, ir_node.Constant)): 
            if (isinstance(expr.opt, ast.Eq)): 
                return ir_node.Constant(lhs.value == rhs.value) 

            elif (isinstance(expr.opt, ast.Add)): 
                if (lhs.type() is str or rhs.type() is str): 
                    return ir_node.Constant(lhs.value + rhs.value) 
                
                elif (lhs.type() in [int, float] and rhs.type() in [int, float]): 
                    return ir_node.Constant(lhs.value + rhs.value)

        else: 
            return ir_node.BinaryExpression(expr.opt, lhs, rhs) 

    else: 
        logging.error('[ERROR] unhandled type of expression: {}'.format(expr)) 
        
    # return UnknownConstant if non of the above scenarios apply     
    return ir_node.UnknownConstant

# ====
# Given a Context and a Solution, validate the Solution
# Return a boolean to indicate the validation result 
# ====
def validate_solution (exe_context :ExecutionContext, solution :ir_node.Solution): 
    # clone the ExecutionContext 
    original_exe_context = exe_context 
    exe_context = exe_context.clone() 

    # update the context with the solution 
    for var, val in solution.assignments.items(): 
        exe_context.store[var] = val 

    # define a function to count the total number of leaf variables of a store 
    def count_total_num_leaf_variables_for_store (st): 
        _total_num_leaf_vars = 0 
        for _, _val in st.items():
            _total_num_leaf_vars += ir_node.count_num_leaf_variables(_val) 
        return _total_num_leaf_vars 
    
    # define a function to grab the (partial) solution from the context store 
    def get_solution_from_store (st): 
        partial_soln = ir_node.Solution() 
        for _var, _val in st.items(): 
            if (isinstance(_val, ir_node.Constant) and (not isinstance(_val, ir_node.UnknownConstant))): 
                partial_soln.add(_var, _val) 
        return partial_soln

    # resolve the store of the context 
    partial_store = {}
    total_num_leaf_vars = count_total_num_leaf_variables_for_store(exe_context.store) 
    prev_total_num_leaf_vars = total_num_leaf_vars + 1

    while (prev_total_num_leaf_vars > total_num_leaf_vars): 
        prev_total_num_leaf_vars = total_num_leaf_vars 

        # resolve the context store 
        partial_solution = get_solution_from_store(exe_context.store)
        for var, val in exe_context.store.items(): 
            partial_store[var] = eval_expression_partially_with_solution(val, partial_solution)

        # replace the context store with the resolved store 
        total_num_leaf_vars = count_total_num_leaf_variables_for_store(partial_store) 
        exe_context.store = partial_store 

    # check the conditions of the context 
    partial_solution = get_solution_from_store(exe_context.store)
    for cond in exe_context.conditions: 
        eval_cond = eval_expression_partially_with_solution(cond, partial_solution) 

        if (isinstance(eval_cond, ir_node.Constant) 
            and (not isinstance(eval_cond, ir_node.UnknownConstant)) 
            and (eval_cond.type() is bool and eval_cond.value) 
        ): 
            pass 
        else: 
            return False 

    # return 
    return True 