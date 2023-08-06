
from aitestgen.parser import python_parser 

# ====
# function to analyze 
# ====
@python_parser.analyze() 
def foo (x :str): 
    assert(len(x) == 3)
    assert(x[0:1] == 'x')
    assert(x.endswith('z'))

# ====
# Dummy pytest case 
# ====
def test_1 (): 
    pass 