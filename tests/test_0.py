
from aitestgen.parser import python_parser 

# ====
# function to analyze 
# ====
@python_parser.analyze() 
def foo (x :str): 
    a = x
    a = a + 'x'
    b = a 
    a = a + 'x'
    c = a 
    assert(not (c == '1xx'))

def bar (y :str): 
    pass 

# ====
# Dummy pytest case 
# ====
def test_0 (): 
    pass 