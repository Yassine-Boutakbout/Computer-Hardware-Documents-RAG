import json
from logger.logger import Logger
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings


logger = Logger.get_instance()

# loading config file
logger.info(f"Loading config file")
try:
    config = json.load(open("config/config.json"))
except FileNotFoundError as e:
    logger.warning(f"Config file not found; exception: {str(e)}")


# ------------------------------------------------------------------
# 1️⃣ Load the vector store
# ------------------------------------------------------------------
# Assumes the DB folder created by data_processing.py
chroma = Chroma(
    persist_directory=config["db_path"],
    embedding_function=OllamaEmbeddings(model=config["ollama_model"])
)

# ------------------------------------------------------------------
# 2️⃣ Create a RetrievalQA chain
# ------------------------------------------------------------------
# Prompt that concatenates retrieved chunks + the question
prompt = PromptTemplate(
    template="""
You are a helpful assistant.  Use the following context to answer the question.  
If the answer cannot be found in the context, say you don’t know.

Context:
{context}

Question: {question}

Answer:
""",
    input_variables=["context", "question"]
)

#TODO: improve to use invoke method instead of '__call__()'
chain = RetrievalQA.from_chain_type(
    llm=ChatOllama(model=config["ollama_model"]),  # same as embedding model
    chain_type="stuff",
    retriever=chroma.as_retriever(search_kwargs={"k": 4}), # Gets 4 documents for a query search
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
    input_key="question",        # <-- tell the chain to look for "question"
)
# ------------------------------------------------------------------
# 3️⃣ Helper to run a query
# ------------------------------------------------------------------
def ask(question: str) -> tuple[str, list[str]]:
    result = chain({"question": question})
    answer = result["result"]
    # Build a simple list of source titles
    sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
    return answer.strip(), sources