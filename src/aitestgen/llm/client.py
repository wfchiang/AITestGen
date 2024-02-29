import os 
from abc import ABC, abstractmethod
from typing import Dict, List 
import requests

from .json_2_prompt import generate_prompt_from_json_statements


# ====
# Abstract LLM client 
# ====
class AbstractLLMClient (ABC): 
    def __init__(self) -> None:
        super().__init__() 

    @abstractmethod
    def solve_json_statements (json_statements :List) -> Dict: 
        pass 
        

# ====
# ChatGPT client 
# ====
class ChatGPTClient (AbstractLLMClient): 
    def __init__(
            self, 
            openai_api_key :str=None, 
            model :str='gpt-3.5-turbo', 
            endpoint_url :str="https://api.openai.com/v1/chat/completions", 
            default_max_tokens :int=256
    ) -> None:
        super().__init__()

        self.openai_url = endpoint_url

        # configure openai authentication 
        if (type(openai_api_key) is not str): 
            openai_api_key = os.environ.get('OPENAI_API_KEY') 
        assert(type(openai_api_key) is str)
        self.openai_api_key = openai_api_key

        # configure parameters 
        self.model = model 
        self.default_max_tokens = default_max_tokens 
        self.temperature = 0.0 

    def solve_json_statements(
            self, 
            json_statements: List, 
            max_tokens :int=None
    ) -> Dict:
        # generate the prompt from the execution context 
        prompt = generate_prompt_from_json_statements(json_statements=json_statements)

        # call ChatGPT for the answer 
        chatgpt_reps = requests.post(
            self.openai_url, 
            headers={
                'Authorization': 'Bearer ' + self.openai_api_key
            }, 
            json={
                'model': self.model, 
                "messages": [
                    {"role": "user", "content": prompt}
                ], 
                'max_tokens': (max_tokens if (type(max_tokens) is int and max_tokens > 0) else self.default_max_tokens), 
                'temperature': self.temperature
            }
        ) 
        assert(chatgpt_reps.status_code == 200), f"Failed to call OpenAI ({chatgpt_reps.status_code}): {chatgpt_reps.content}"

        chatgpt_reps = chatgpt_reps.json() # get the response payload 

        # retrieve ChatGpt's top-choice answer 
        assert(isinstance(chatgpt_reps, Dict)) 
        assert('choices' in chatgpt_reps)
        assert(len(chatgpt_reps['choices']) > 0) 

        top_chatgpt_choice = chatgpt_reps['choices'][0] 
        assert(isinstance(top_chatgpt_choice, Dict) and 'message' in top_chatgpt_choice)
        chatgpt_saying = top_chatgpt_choice['message']["content"] 

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

        # return 
        return var_name_2_str_val 

    