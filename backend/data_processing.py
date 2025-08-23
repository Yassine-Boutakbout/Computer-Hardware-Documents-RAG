import os
import json
from logger.logger import Logger
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader


logger = Logger.get_instance()


class DataProcessing():
    __instance = False

    @classmethod
    def launch_processing(cls):
        if not cls.__instance:
            __DataProcessing()
            cls.__instance = True
            return cls.__instance

class __DataProcessing():

    async def Processing():
        logger.info("Starting Data Processing service")

        # loading config file
        logger.info(f"Loading config file")
        try:
            config = json.load(open("config/config.json"))
        except FileNotFoundError as e:
            logger.warning(f"Config file not found; exception: {str(e)}")

        logger.debug(f"Configuration: {config}")

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
        logger.info(f"Store Embeddings in local DB, path: {config['db_path']}, please wait...")
        chroma_client = await Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=config["db_path"]
        )
        logger.info("Data Processing finished successfully")

# Testing the embeddings
# if __name__ == "__main__":
#     __DataProcessing().Processing()
#     print("Data processing complete.  Embeddings stored in ChromaDB.")