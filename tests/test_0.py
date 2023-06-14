
from aitestgen.parser import python_parser 

# ====
# function to analyze 
# ====
@python_parser.analyze() 
def foo (x :str): 
    assert(x[0:3] == "xyz")

# ====
# Dummy pytest case 
# ====
def test_0 (): 
    pass 