import random
import string
import docker
import os

def random_name():
    """Generate a random name."""
    verbs = [
        "debugging",
        "coding",
        "testing",
        "deploying",
        "optimizing",
        "refactoring",
        "documenting",
        "integrating",
        "automating",
        "scripting",
        "compiling",
        "parsing",
        "querying",
        "analyzing",
        "implementing",
        "designing",
    ]
    nouns = [
        "developer",
        "programmer",
        "engineer",
        "coder",
        "architect",
        "tester",
        "analyst",
        "scripter",
        "maintainer",
        "integrator",
        "optimizer",
        "refactorer",
        "designer",
        "implementer",
        "compiler",
    ]
    return random.choice(verbs) + "_" + random.choice(nouns)

def generate_dockerfile(requirements):
    """Generate a Dockerfile for the given requirements and local main.py."""
    dockerfile = f"""FROM python:3.13-slim

RUN pip install {requirements}

COPY main_app.py /main.py
WORKDIR /
CMD ["python3", "/main.py"]
"""
    return dockerfile

def expand_newlines(s):
    return s.encode('utf-8').decode('unicode_escape')

# Flask app code to write to main.py

def create_build_function(code, name=None):
    """
    Creates and builds a new edge function.
    """
    code = expand_newlines(code)
    # Generate a random name for the Docker image
    if name is None:
        name = random_name()
    # Write the main.py file
    with open("main_app.py", "w") as code_file:
        code_file.write(code)
    # Write the Dockerfile
    dockerfile = generate_dockerfile("flask")
    with open("Dockerfile", "w") as file:
        file.write(dockerfile)
    # Initialize Docker client
    dockerclient = docker.from_env()
    dockerclient.images.build(path=".", tag=f"envybase:{name}_runtime")
    #remove the Dockerfile and main.py
    os.remove("Dockerfile")
    os.remove("main_app.py")
    
