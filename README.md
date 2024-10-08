# AI-Test-Gen 

This tool, AI-Test-Gen, use generative AI to generate string values satisfying the given constraints. 
In other words, it generates string-type test cases. 

Let's say we have a "puzzle" here: 
* variable `xyz` is equal to variable `abc`
* variable `xyz` starts with `"www"` and ends with `".net"` 
* find me a value of variable `abc` satisfies the above conditions 

AI-Test-Gen will solve the above puzzle and tell you `"www.example.net"` is a value for variable `abc` to satisfy the conditions. 

* Ok, ok, I got it. Theorem prover like Z3 and CVC5 are the "serious" tools for this kind of "SMT puzzles". 

* And, yes, I understand no rational inferences happen in current generative AI. 

But, hey, why don't we give generative AI a shot? 
Probably it can fast solve complex problems accidentally by linear algebra. 
I am not saying that AI-Test-Gen is a killer tool to replace theorem provers like Z3 and CVC5. 
I am just curious how far generative AI can go. 

## Online demo 

1. Acquire an OpenAI API key... sorry, it only supports OpenAI for now. 
2. Go to web app [https://aitestgen-otbcpwzrta-uk.a.run.app](https://aitestgen-otbcpwzrta-uk.a.run.app)
3. Specify your OpenAPI key in the web app. I don't steal your API key. 
4. Enter the following "JSON statements", and hit "Generate!"
    ```JSON
    [
        [":=", ["var", "xyz"], ["var", "abc"]], 
        ["assert", ["startsWith", ["var", "xyz"], "www"]], 
        ["assert", ["endsWith", ["var", "xyz"], ".net"]]
    ]
    ```
5. In the above "JSON statements" (puzzle), `abc` is the only unbounded variable. So AI-Test-Gen will only display the solution for it. E.g., `abc_1` (a unique name given to variable `abc`) is `www.example.net`. 

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

Create a `.env` with... 

```BASH 
OPENAI_API_KEY=<your_openai_api_hey>
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
poetry build
``` 

then 

```BASH
poetry publish -r google 
```