# Computer Hardware documents RAG based system

## Introduction
In this repo we re going to setup a system that uses basic rag techniques to search through a documents based on a user query question.


## Setup backend environment
1. Python: You're likely to have Python already. If not, download the latest version from https://www.python.org/downloads/. Make sure to check the box "Add Python to PATH" during installation.

2. Pip: Pip is Python's package installer. It should come with your Python installation. You can check if you have it by opening a terminal/command prompt and typing pip --version

3. Creating a Virtual Environment (Highly Recommended) :
- Open your terminal/command prompt.
- Navigate to the directory where you want to create your project (e.g., cd Documents/rag-docs).
- Create a virtual environment: python -m venv .venv (This creates a folder named .venv in your project directory).
- Activate the virtual environment (in your commandline prompt):

  Windows: ```.venv\Scripts\activate```

  macOS/Linux: ```source .venv/bin/activate```

4. Installing the Dependencies
With your virtual environment activated, use pip to install the packages:
```
pip install -r backend\requirements.txt
```
* Flask: For building the API.
* Pydantic: For data validation and serialization.
* Streamlit: For the frontend.
* Langchain: The core RAG framework.
* ChromaDB: The vector database.

5. Verifying Installations

After the installation completes, it's a good idea to check that the packages are installed correctly:

* Python: python --version (Should show the Python version you installed)
* Pip: pip --version (Should show the Pip version)

You can also try importing the packages in a Python interpreter:
```
python
>>> import flask
>>> import pydantic
>>> import streamlit
>>> import langchain
>>> import chromadb
>>> import openai
```
If no errors occur, the installation was successful.