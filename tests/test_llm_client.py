import os 
from aitestgen.llm.client import ChatGPTClient 

from utils import get_fresh_exe_context

import logging
logging.basicConfig(level=logging.INFO)

# ====
# Tests for generate_prompt_from_json_statements
# ====
def test_client_0 (): 
    get_fresh_exe_context() 

    openai_api_key = os.environ.get("OPENAI_API_KEY", None) 
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
    