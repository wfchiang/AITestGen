from aitestgen.ir import node as ir_node 

def test_parse_json_to_expression_0 (): 
    json_expr = 1 
    expr = ir_node.parse_json_to_expression(json_obj=json_expr) 
    assert(isinstance(expr, ir_node.Constant))
    assert(expr.type is int)
    assert(expr.value == 1)

    json_expr = "abc"
    expr = ir_node.parse_json_to_expression(json_obj=json_expr)
    assert(isinstance(expr, ir_node.Constant))
    assert(expr.type is str and expr.value == "abc")

def test_parse_json_to_expression_1 (): 
    json_expr = ["not", True]
    expr = ir_node.parse_json_to_expression(json_obj=json_expr) 
    assert(isinstance(expr, ir_node.UnaryExpression))
    assert(expr.to_natural_language() == "not true")

def test_parse_json_to_expression_2 (): 
    json_expr = ["startsWith", "xyz", "abc"]
    expr = ir_node.parse_json_to_expression(json_obj=json_expr) 
    assert(isinstance(expr, ir_node.StringOperation))
    assert(expr.to_natural_language() == '"xyz" starts with "abc"')

def test_parse_json_to_expression_3 (): 
    json_expr = ["==", "xyz", "abc"]
    expr = ir_node.parse_json_to_expression(json_obj=json_expr) 
    assert(isinstance(expr, ir_node.BinaryExpression))
    assert(expr.to_natural_language() == '"xyz" is the same as "abc"')