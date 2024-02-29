from aitestgen.ir import node as ir_node 
from aitestgen.ir.interpreter import ExecutionContext 

def get_fresh_exe_context (): 
    ir_node.NEXT_VARIABLE_ID = 0
    return ExecutionContext() 