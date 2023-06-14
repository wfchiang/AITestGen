
from aitestgen.ir import node 

# ====
# function to analyze 
# ====
def foo (x :str): 
    assert(x[0:3] == "xyz")

# ====
# Dummy pytest case 
# ====
def test_0 (): 
    pass 