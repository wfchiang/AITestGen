import ast 
import logging
from ..ir import node as ir_node 
from ..ir import symbolic_executor as se 

# ==== 
# Globals 
# ====
logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO) 

# ====
# Generation helper functions 
# ====
# Given an Expression, generate a sentence describes that Expression 
# Return None if failed to generate a sentence...
def generate_sentence_from_expression (expr :ir_node.Expression, is_negated :bool): 
    assert(isinstance(expr, ir_node.Expression)) 
    assert(type(is_negated) is bool)

    generated_sent = None 

    if (isinstance(expr, ir_node.Constant)): 
        generated_sent = str(expr) 

    elif (isinstance(expr, ir_node.Variable)): 
        generated_sent = str(expr) 

    elif (isinstance(expr, ir_node.UnaryExpression)): 
        if (isinstance(expr.opt, ast.Not)): 
            generated_sent = generate_sentence_from_expression(expr.operand, (not is_negated))

        else: 
            logger.error('Unsupported UnaryExpression: {}'.format(expr))

    elif (isinstance(expr, ir_node.BinaryExpression)): 
        lhs_generated_sent = generate_sentence_from_expression(expr.lhs, is_negated) 
        rhs_generated_sent = generate_sentence_from_expression(expr.rhs, is_negated)
        
        if (lhs_generated_sent is not None and rhs_generated_sent is not None): 
            if (isinstance(expr.opt, ast.Add)): 
                generated_sent = f'{lhs_generated_sent} appended by {rhs_generated_sent}'
            
            elif (isinstance(expr.opt, ast.Eq)): 
                generated_sent = '{} {} {}'.format(
                    lhs_generated_sent, 
                    ('is not equal to' if (is_negated) else 'is equal to'), 
                    rhs_generated_sent
                )

            else: 
                logger.error('Unsupported BinaryExpression: {}'.format(expr)) 

    else: 
        assert(False), 'Invalid expr for generate_sentence_from_expression: {}'.format(expr) 

    return generated_sent 

# Given a store entry of ExecutionContext, generate a sentence 
def generate_sentence_from_store_entry (var :ir_node.Variable, val :ir_node.Expression): 
    assert(isinstance(var, ir_node.Variable))
    assert(isinstance(val, ir_node.Expression))

    if (isinstance(val, ir_node.UnknownConstant)):
        return None 

    else: 
        return generate_sentence_from_expression(
            ir_node.BinaryExpression(
                opt=ast.Eq(), 
                lhs=var, 
                rhs=val, 
            ), 
            is_negated=False 
        )

# ====
# Given an ExecutionContext, generate a completed prompt for LLM to solve the unknown values 
# ====
# Generate sentences from the context 
def generate_sentences_from_execution_context (exe_context :se.ExecutionContext): 
    assert(isinstance(exe_context, se.ExecutionContext)) 

    # generate sentences from store 
    store_sentences = []
    for var, val in exe_context.store.items(): 
        store_sent = generate_sentence_from_store_entry(var, val) 
        if (store_sent is not None):
            store_sentences.append(store_sent)

    # generate sentences from conditions 
    condition_sentences = []
    for cond in exe_context.conditions: 
        condition_sent = generate_sentence_from_expression(cond, is_negated=False) 
        if (condition_sent is not None): 
            condition_sentences.append(condition_sent) 

    # return 
    return {
        'store': store_sentences, 
        'conditions': condition_sentences
    }

# Generate a single prompt for LLM to solve the unknown variables 
EMPTY_PROMPT = 'No task for you. '
def generate_prompt_from_execution_context (exe_context :se.ExecutionContext): 
    assert(isinstance(exe_context, se.ExecutionContext))

    final_prompt = '' 

    # collect context information 
    all_vars = exe_context.store.keys() 

    unbound_vars = list(map(
        lambda kv: kv[0], 
        list(filter(
            lambda kv: isinstance(kv[1],ir_node.UnknownConstant), 
            exe_context.store.items()
        ))
    ))

    # if there is no unbound variables, why are we here? 
    if (len(unbound_vars) == 0): 
        return EMPTY_PROMPT
    
    assert(len(all_vars) > 0)
    
    # the "system" instruction/message 
    all_vars_sent = (
        'There is only one variable, {}, in the system. '.format(str(all_vars[0]))
        if (len(all_vars) == 1) 
        else 'Here are the variables in the system: {}. '.format(', '.join([str(v) for v in all_vars]))
    )

    final_prompt += """
You are a rational thinker. You will be given a relation system of string variables, and find possible texts for the unknown variables. 
{} 
""".format(all_vars_sent)

    # generate sentences from the context 
    exe_context_sents = generate_sentences_from_execution_context(exe_context) 

    constraint_sents = exe_context_sents['store'] + exe_context_sents['conditions']

    final_prompt += """
Here are the relations among the string variables. 
{}
""".format(' \n'.join(constraint_sents))

    # the request passage 
    answer_template_sent = '\n'.join(
        ['{} = <answer> '.format(str(v)) for v in unbound_vars]
    )

    unbound_vars_sent = (
        '' 
        if (len(unbound_vars) == 0) 
        else (
            'Now, find the possible text for string variable {}'.format(str(unbound_vars[0]))
            if (len(unbound_vars) == 1) 
            else 'Now, find the possible texts for string variables: {}'.format(', '.join([str(v) for v in unbound_vars]))
        )
    )

    final_prompt += """
You must respect the afore given constraints. 
You must only provide concrete examples as brief answers. 
You must answer in brief in the following format: 
{}
{}
""".format(answer_template_sent, unbound_vars_sent)

    # DEBUG 
    print(final_prompt)

    # return 
    return final_prompt 

