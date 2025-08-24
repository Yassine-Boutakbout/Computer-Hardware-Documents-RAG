# Computer Hardware documents RAG based system

## Introduction
In this repo we re going to setup a system that uses basic rag techniques to search through a documents based on a user query question.


## Setup backend environment
1. Python: You're likely to have Python already. If not, download the latest version from https://www.python.org/downloads/. Make sure to check the box "Add Python to PATH" during installation.

2. Pip: Pip is Python's package installer. It should come with your Python installation. You can check if you have it by opening a terminal/command prompt and typing pip --version

3. Creating a Virtual Environment (Highly Recommended) :
- Open your terminal/command prompt.
- Navigate to the directory where you want to create your project (e.g., cd Documents/rag-docs).
- Create a virtual environment: ```python -m venv .venv ```(This creates a folder named .venv in your project directory).
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

## RAG‑powered Question‑Answer API

This service exposes a single HTTP endpoint that accepts a natural‑language question and returns an answer that is generated only from the knowledge base stored in the RAG vector store.
All requests and responses are JSON‑encoded and the API follows a REST style.

Base URL – http://<host>:<port>
(e.g. http://localhost:5000 when running locally)

1️⃣ /ask

Property	Value

Method	POST

URL	/ask

Description	Submit a question and receive an answer that is based exclusively on the indexed knowledge base.

Request 
```
Field: question
Type: string
Required: True
Description: The natural‑language question you want answered.
```
Example (JSON body)
```
{
  "question": "What is RAM?"
}
```
cURL
```
curl -X POST "http://localhost:5000/ask" \
     -H "Content-Type: application/json" \
     -d 'What is RAM?'
```
Response
```
Fields: answer, sources	
Type: string, array[string]
Description: **answer** The generated answer. **sources** (Optional) List of source document identifiers or titles that were used to construct the answer. The current implementation returns an empty array – the pipeline can be extended to surface document IDs.
```
Success Response (200 OK)
```
{
  "answer": "<think>\nOkay, the user is asking, \"What is RAM?\" Let me check the provided context to find the answer.\n\nLooking at the context, there's a mention of RAM and ROM in question 9. The context says, \"What are the differences between and uses of RAM and ROM?\" So, the answer should be about the differences and uses of RAM and ROM. However, the user is specifically asking about RAM, not ROM. \n\nThe context doesn't go into the details of what RAM is. It talks about their differences and uses. Since the question is about the definition of RAM, and the context doesn't provide that information, I need to determine if the answer can be found here. \n\nThe user's question is straightforward, but the context only discusses the differences between RAM and ROM. There's no direct explanation of what RAM is. Therefore, based on the given context, the answer can't be found. The assistant should state that the answer isn't in the context.\n</think>\n\nThe answer cannot be found in the provided context. The context discusses the differences between RAM and ROM but does not define RAM or provide detailed information about its characteristics.",
    "sources": [
        "data\\docs\\88394_ch03_savage.pdf",
        "data\\docs\\88394_ch03_savage.pdf",
        "data\\docs\\SBS1104.pdf",
        "data\\docs\\SBS1104.pdf"
    ]
}
```

2️⃣ /health (optional)

Property	Value

Method	GET

URL	/health

Description	Simple health‑check endpoint that returns the service status.

Success Response (200 OK)
```
{"status":"healthy"}
```
3️⃣ / (root)
Property	Value
Method	GET
URL	/
Description	Returns a friendly greeting or brief description of the service.
Response
Status Code	Body
200 OK	{"message":"RAG QA Service – ready to answer questions."}