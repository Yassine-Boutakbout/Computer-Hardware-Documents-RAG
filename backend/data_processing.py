import os
import json
from logger.logger import Logger
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader


logger = Logger.get_instance()

# loading config file
logger.info(f"Loading config file")
try:
    config = json.load(open("config/config.json"))
except FileNotFoundError as e:
    logger.warning(f"Config file not found; exception: {str(e)}")

# Loading Documents
logger.info("Loading PDF files")
try:
    loader = DirectoryLoader(config["data_path"], glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
except Exception as e:
    logger.warning(f"An exception occured while loading pdf files, more details: {str(e)}")

# Chunking the Documents using our predefined chunk size and overlap (Experiment with these values)
logger.info("Chunking Documents")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=config["chunk_size"], chunk_overlap=config["chunk_overlap"])
chunks = text_splitter.split_documents(documents)

# Creating Embeddings
# Example using OllamaEmbeddings: All You'll need is to install Ollama and run it with the model you want to use.
embeddings = OllamaEmbeddings(model=config["ollama_model"]) #Change the model name if needed.

# 4. Store Embeddings in ChromaDB
logger.info("Store Embeddings in local DB")
chroma_client = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="db"
)


# Testing the embeddings
if __name__ == "__main__":
    print("Data processing complete.  Embeddings stored in ChromaDB.")