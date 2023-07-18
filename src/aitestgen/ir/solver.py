from ..ir.symbolic_executor import Executor, ExecutionContext
from ..llm.client import ChatGPTClient 

# ==== 
# find solutions/test-cases for the unbounded variables 
# Returns a list of context-solution pair: [(context_1, solution_1), (context_2, solution_2), ...]
# Each context is an ExecutionContext 
# Each solution is a map of variable->(str-)value
# ====
def solve_for_test_cases (exe_context :ExecutionContext): 
    # symbolically execute the code to explore the final contexts 
    symbolic_executor = Executor() 
    final_contexts = symbolic_executor.execute(exe_context) 

    # solve for the test-cases 
    chatgpt_client = ChatGPTClient() 
    context_solution_list = [] 
    for f_ctx in final_contexts: 
        sol = chatgpt_client.solve_context(f_ctx) 
        context_solution_list.append((f_ctx, sol)) 

    # return 
    return context_solution_list 