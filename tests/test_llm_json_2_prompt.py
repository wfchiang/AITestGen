from aitestgen.llm import json_2_prompt

from utils import get_fresh_exe_context

import logging
logging.basicConfig(level=logging.INFO)

# ====
# Tests for generate_prompt_from_json_statements
# ====
def test_generate_prompt_from_json_statements_0 (): 
    get_fresh_exe_context() 

    final_prompt = json_2_prompt.generate_prompt_from_json_statements(
        json_statements=[
            [":=", ["var", "xyz"], ["var", "abc"]], 
            ["assert", ["startsWith", ["var", "abc"], "www"]]
        ]
    )

    # logging.info(final_prompt)
    