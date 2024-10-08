import os 
from abc import ABC, abstractmethod
from typing import Dict, List 

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser 
from langchain_openai.chat_models import ChatOpenAI

from .json_2_prompt import SYSTEM_MESSAGE, generate_prompt_from_json_statements

import logging 
logging.basicConfig(level=logging.INFO)


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
            endpoint_url :str=None, # "https://api.openai.com/v1/chat/completions", 
            default_max_tokens :int=256
    ) -> None:
        super().__init__()

        # configure openai authentication 
        if (type(openai_api_key) is not str): 
            openai_api_key = os.environ.get('OPENAI_API_KEY') 
        assert(type(openai_api_key) is str)
        self.openai_api_key = openai_api_key

        # configure parameters 
        self.model = model
        self.openai_url = endpoint_url 
        self.default_max_tokens = default_max_tokens 
        self.temperature = 0.0 

        # build the LLM chain 
        self.prompt_template = ChatPromptTemplate.from_messages(
            messages=[
                ("system", SYSTEM_MESSAGE), 
                ("human", "{statements}")
            ]
        )
        
        self.llm = ChatOpenAI(
            model=self.model, 
            temperature=self.temperature,
            api_key=self.openai_api_key, 
            max_tokens=self.default_max_tokens,  
            base_url=self.openai_url, 
            verbose=True
        )

        self.output_parser = StrOutputParser() 

        self.llm_chain = self.prompt_template | self.llm | self.output_parser 

    def solve_json_statements(
            self, 
            json_statements: List, 
            max_tokens :int=None
    ) -> Dict:
        # generate the prompt from the execution context 
        prompt = generate_prompt_from_json_statements(json_statements=json_statements)

        # call ChatGPT for the answer 
        chatgpt_saying = self.llm_chain.invoke({
            "statements": prompt
        })

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

    