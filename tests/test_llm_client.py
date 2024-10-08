import os 
from dotenv import load_dotenv
from aitestgen.llm.client import ChatGPTClient 

from utils import get_fresh_exe_context

import logging
logging.basicConfig(level=logging.INFO)

load_dotenv() 

# ====
# Tests for generate_prompt_from_json_statements
# ====
def test_client_0 (): 
    get_fresh_exe_context() 

    openai_api_key = os.environ["OPENAI_API_KEY"] 
    if (type(openai_api_key) is str): 
        client = ChatGPTClient(openai_api_key=openai_api_key)

        solution = client.solve_json_statements(
            json_statements=[
                [":=", ["var", "xyz"], ["var", "abc"]], 
                ["assert", ["startsWith", ["var", "xyz"], "www"]]
            ]
        )

        logging.info(f"{solution = }")

        assert("abc_1" in solution) 
        assert(solution["abc_1"].startswith("www"))

    else:
        assert(False), f"Skipped because OPENAI_API_KEY is not set"

def test_client_1 (): 
    get_fresh_exe_context() 

    openai_api_key = os.environ["OPENAI_API_KEY"] 
    if (type(openai_api_key) is str): 
        client = ChatGPTClient(openai_api_key=openai_api_key)

        solution = client.solve_json_statements(
            json_statements=[
                [":=", ["var", "xyz"], ["var", "abc"]], 
                ["assert", ["startsWith", ["var", "xyz"], "www"]], 
                ["assert", ["endsWith", ["var", "xyz"], ".net"]]
            ]
        )

        logging.info(f"{solution = }")

        assert("abc_1" in solution) 
        assert(solution["abc_1"].startswith("www"))

    else:
        assert(False), f"Skipped because OPENAI_API_KEY is not set"
        