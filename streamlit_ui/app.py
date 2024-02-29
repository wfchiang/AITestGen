import streamlit as st 
import json 
import traceback 
import pandas 

from aitestgen.llm.client import ChatGPTClient 

import logging
logging.basicConfig(level=logging.INFO)

# Display the title 
st.title('AI Test Generation -- Demo')

# The textbox for the OpenAI token 
openai_api_key = '' 
if ('OPENAI_API_KEY' in st.session_state): 
    openai_api_key = st.session_state['OPENAI_API_KEY'] 

openai_api_key = st.text_input('OpenAI API Key: ', openai_api_key)

# The text area for capturing the Pythong code 
json_statements_str = st.text_area('Enter JSON statements here: ') 
go_generating = st.button('Generate!') 
error_message = None 

# Init the solutions 
if ('solution' not in st.session_state):
    st.session_state['solution'] = None 

# Validate the json statements 
json_statements = None 
if (type(json_statements_str) is str and json_statements_str.strip() != ""): 
    try: 
        json_statements = json.loads(json_statements_str)
    except: 
        st.error("Syntax error in the JSON statements")
        json_statements = None 

go_generating = (go_generating and type(json_statements) is list) 

# go generate solutions 
if (go_generating): 
    exe_context = None 

    # check for the OpenAI API Key 
    if (openai_api_key is None or openai_api_key.strip() == ''): 
        error_message = 'No OpenAI API Key provided...'
    
    else: 
        gpt_client = ChatGPTClient(
            openai_api_key=openai_api_key
        )

        try: 
            gpt_solutions = gpt_client.solve_json_statements(json_statements=json_statements) 
            st.session_state["solution"] = gpt_solutions

        except Exception as ex: 
            traceback.print_exc()
            error_message = "Unexpected error occurred while calling GPT... {ex}"
        
# display the error message 
if (error_message is not None): 
    st.error(error_message)

# display the solutions 
if (type(st.session_state["solution"]) is not dict): 
    st.write("No solution to display...")

else: 
    df_rows = [] 
    for var, val in st.session_state["solution"].items(): 
        df_rows.append({
            "variable": str(var), 
            "value": val
        })
    st.header(f'Solution: ')
    st.dataframe(pandas.DataFrame(df_rows))
