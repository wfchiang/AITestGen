import streamlit as st 
import traceback 
import pandas 
import aitestgen.parser.python_parser as python_parser 
from aitestgen.ir.symbolic_executor import ExecutionContext 
import aitestgen.ir.solver as solver 

# Display the title 
st.title('AI Test Generation -- Demo')

# The textbox for the OpenAI token 
openai_api_key = '' 
if ('OPENAI_API_KEY' in st.session_state): 
    openai_api_key = st.session_state['OPENAI_API_KEY'] 

openai_api_key = st.text_input('OpenAI API Key: ', openai_api_key)

# The text area for capturing the Pythong code 
python_source_code = st.text_area('Python code (function) to generate test cases for: ') 
go_generating = st.button('Generate!') 
error_message = None 

# Init the solutions 
if ('solutions' not in st.session_state):
    st.session_state['solutions'] = [] 

# go generate solutions 
if (go_generating): 
    exe_context = None 

    # check for the OpenAI API Key 
    if (openai_api_key is None or openai_api_key.strip() == ''): 
        error_message = 'No OpenAI API Key provided...'
    
    else: 
        # parse the given python source code 
        try: 
            exe_context = python_parser.parse_source_code_to_symbolic_execution_context(python_source_code)
        except: 
            traceback.print_exc() 
            error_message = """Failed to parse the python source code to ExecutionContext...
            {}
            """.format(python_source_code)
        
        # explore the solutions 
        if (isinstance(exe_context, ExecutionContext)): 
            context_solution_list = [] 
            try: 
                context_solution_list = solver.solve_for_test_cases(exe_context, openai_api_key=openai_api_key)
            except: 
                traceback.print_exc() 
                error_message = """Failed to solve the ExecutionContext for test cases...""" 

            # retrieve the solutions 
            ir_solutions = [sol for _, sol in context_solution_list] 
            solutions = [
                [{'Variable': str(var), 'Value': val.value} for var, val in sol.assignments.items()]
                for sol in ir_solutions
            ] 
            st.session_state['solutions'] = solutions 

# display the error message 
if (error_message is not None): 
    st.error(error_message)

# display the solutions 
solutions = st.session_state['solutions'] 
if (len(solutions) > 0): 
    for i_soln, soln in enumerate(solutions): 
        df_soln = pandas.DataFrame(soln) 
        st.header(f'Test Case {i_soln+1}')
        st.dataframe(df_soln)
