# AITestGen 

This is about AI driven test generation. 
The proof-of-concept is implemented in Python. 

### Running the web application

Under directory `web_app`, run: 

```BASH 
streamlit run app.py 
```

### Unit-testing with PyTest 

First setup your own OpenAI key: 

```BASH 
export OPENAI_API_KEY=<your_openai_api_hey>
```

Then run Pytest: 

```BASH 
pytest -s tests 
``` 
