
from aitestgen.parser import python_parser 

# ====
# function to analyze 
# ====
@python_parser.analyze() 
def foo (x :str): 
    a = x
    a = a + 'k'
    b = a 
    a = a + 'k'
    c = a 
    assert(not (c == 'okk'))
    assert(b == 'ok')

def bar (y :str): 
    pass 

# ====
# Dummy pytest case 
# ====
def test_0 (): 
    pass 