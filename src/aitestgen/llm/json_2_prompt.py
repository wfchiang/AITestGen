from typing import List 
from ..ir.node import Statement
from ..ir.interpreter import ExecutionContext, interpret_json_statement

import logging
logging.basicConfig(level=logging.INFO)

# ==== 
# Globals 
# ====

# ====
# Json statement execution 
# ====
def execute_json_statements (json_statements :List) -> ExecutionContext: 
    assert(isinstance(json_statements, List))

    exe_context = ExecutionContext() 

    for json_stat in json_statements: 
        exe_context = interpret_json_statement(
            json_obj=json_stat, 
            exe_context=exe_context
        )

    return exe_context

# ====
# Dump an execution context to sentences 
# ====
def dump_execution_context_to_sentences (exe_context :ExecutionContext) -> List[str]: 
    sents = [] 

    for stat in exe_context.executed_statements: 
        assert(isinstance(stat, Statement))
        sents.append(stat.to_natural_language())

    return sents 

# ====
# Generate LLM prompt from Json statements 
# ====
def generate_prompt_from_json_statements (json_statements :List) -> str: 
    final_prompt = "" 

    # "Execute" the json statement 
    exe_context = execute_json_statements(json_statements)
    assert(isinstance(exe_context, ExecutionContext))

    # if there is no unbound variables, why are we here? 
    if (len(exe_context.unbounded_variables) == 0): 
        return f"No task for you since there is no unbounded variables."
    
    unbound_vars = exe_context.unbounded_variables
    
    # the "system" instruction/message 
    all_vars = list(exe_context.store.keys()) 
    all_vars_sent = (
        'There is only one variable, {}, in the system. '.format(str(all_vars[0]))
        if (len(all_vars) == 1) 
        else 'Here are the variables in the system: {}. '.format(', '.join([str(v) for v in all_vars]))
    )

    final_prompt += f"""
You are a rational thinker. You will be given a relation system of string variables, and find possible texts for the unknown variables. 
{all_vars_sent} 
"""

    # generate sentences from the context 
    exe_context_sents = dump_execution_context_to_sentences(exe_context) 
    exe_context_sents = list(map(lambda s: f"- {s.strip()}", exe_context_sents))

    final_prompt += """
Here are the relations among the string variables. 
{}
""".format("\n".join(exe_context_sents))

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

    final_prompt += f"""
You must respect the afore given constraints. 
You must only provide concrete examples as brief answers. 
You must answer in brief in the following format: 
{answer_template_sent}

{unbound_vars_sent}
"""

    # DEBUG 
    # print(final_prompt)

    # return 
    return final_prompt 

