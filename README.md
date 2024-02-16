# AITestGen 

This is about AI driven test generation. 
The proof-of-concept is implemented in Python. 

### Running the web application

Under directory `web_app`, run: 

```BASH 
streamlit run app.py 
```

## Notes for me 

### Unit-testing with PyTest 

First setup your own OpenAI key: 

```BASH 
export OPENAI_API_KEY=<your_openai_api_hey>
```

Then run Pytest: 

```BASH 
pytest -s tests 
``` 

### Publish Python Package 

**One-time Setup**

1. Install python dependencies 
    ```BASH
    pip install twine 
    ```
    ```BASH
    pip install keyrings.google-artifactregistry-auth
    ```

2. Configure poetry 
    ```BASH 
    poetry config repositories.google https://us-east1-python.pkg.dev/wfchiang-dev/python-repo/
    ```

**Publication command**

```BASH
poetry publish -r google 
```