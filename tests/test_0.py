
from aitestgen.parser import python_parser 

# ====
# function to analyze 
# ====
@python_parser.analyze() 
def foo (x :str): 
    a = x
    a = a + '2'
    b = a 
    a = a + '3'
    c = a 
    assert(not (c == '123'))
    assert(b == '32')

def bar (y :str): 
    pass 

# ====
# Dummy pytest case 
# ====
def test_0 (): 
    pass 