import os 
from abc import ABC, abstractmethod
from typing import Dict
import openai 

from ..ir import node as ir_node 
from ..ir.symbolic_executor import ExecutionContext

from ..parser import ir_2_llm_prompt 

# ====
# Abstract LLM client 
# ====
class AbstractLLMClient (ABC): 
    def __init__(self) -> None:
        super().__init__() 

    @abstractmethod
    def solve_context (exe_context :ExecutionContext) -> Dict: 
        pass 
        

# ====
# ChatGPT client 
# ====
class ChatGPTClient (AbstractLLMClient): 
    def __init__(
            self, 
            model :str='text-davinci-003', 
            default_max_tokens :int=256
    ) -> None:
        super().__init__()

        # configure openai authentication 
        openai_api_key = os.environ.get('OPENAI_API_KEY') 
        assert(type(openai_api_key) is str)
        openai.api_key = openai_api_key 

        # configure parameters 
        self.model = model 
        self.default_max_tokens = default_max_tokens 
        self.temperature = 0.0 

    def solve_context(
            self, 
            exe_context: ExecutionContext, 
            max_tokens :int=None
    ) -> Dict:
        # generate the prompt from the execution context 
        prompt = ir_2_llm_prompt.generate_prompt_from_execution_context(exe_context) 

        # call ChatGPT for the answer 
        chatgpt_reps = openai.Completion.create(
            model=self.model, 
            prompt=prompt, 
            max_tokens=(max_tokens if (type(max_tokens) is int and max_tokens > 0) else self.default_max_tokens), 
            temperature=self.temperature
        )

        # retrieve ChatGpt's top-choice answer 
        assert(isinstance(chatgpt_reps, Dict)) 
        assert('choices' in chatgpt_reps)
        assert(len(chatgpt_reps['choices']) > 0) 

        top_chatgpt_choice = chatgpt_reps['choices'][0] 
        assert(isinstance(top_chatgpt_choice, Dict) and 'text' in top_chatgpt_choice)
        chatgpt_saying = top_chatgpt_choice['text'] 

        # parase ChatGPT's answer 
        saying_lines = chatgpt_saying.split('\n')
        saying_lines = list(map(lambda x: x.strip(), saying_lines))
        saying_lines = list(filter(lambda x: len(x) > 0, saying_lines)) 

        var_name_2_str_val = {} 
        for saying in saying_lines: 
            i = saying.find('=') 
            if (i > 0): 
                var_name = saying[0:i].strip() 
                val = saying[i+1:].strip().strip('"') 
                var_name_2_str_val[var_name] = val 

        # create a Solution object 
        solution = ir_node.Solution() 
        for var in exe_context.store.keys(): 
            var_name = str(var) 
            if (var_name in var_name_2_str_val): 
                val = ir_node.Constant(var_name_2_str_val[var_name])
                solution.add(var, val)
                continue 

        # return 
        return solution 

    