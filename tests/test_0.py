
from aitestgen.parser import python_parser 

# ====
# function to analyze 
# ====
@python_parser.analyze() 
def foo (x :str): 
    a = x
    # assert(x[0:3] == "xyz")

def bar (y :str): 
    pass 

# ====
# Dummy pytest case 
# ====
def test_0 (): 
    pass 