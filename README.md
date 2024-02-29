# AITestGen 

This is about AI driven test generation. 
The proof-of-concept is implemented in Python. 

## Docker build and run 

**Docker build** 

```BASH
docker build -t aitestgen:0.2.0 .
```

**Docker run** 

```BASH
docker run -p 8000:8000 aitestgen:0.2.0
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

### Publish Docker Images

Make sure `gcloud` is authorized: 

```BASH
gcloud auth configure-docker us-east4-docker.pkg.dev
```

Tag the image as `us-east4-docker.pkg.dev/wfchiang-dev/docker-repo/aitestgen:<version>`, then push it. 

### Publish Python Packages 

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