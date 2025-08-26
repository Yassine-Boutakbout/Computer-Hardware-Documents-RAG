import os
import json
import asyncio
from logger.logger import Logger
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader


logger = Logger.get_instance()


class DataProcessing():
    __instance = False

    @classmethod
    async def launch_processing(cls):
        if not cls.__instance:
            await __DataProcessing().Processing()
            cls.__instance = True
            return cls

class __DataProcessing():

    @staticmethod
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

        # **Add a 'source' metadata field to every chunk**
        #    (the original file name without path)
        for chunk in chunks:
            # If you loaded the PDF via DirectoryLoader, the metadata already contains
            # "source": "path/to/file.pdf".  We'll override it with just the file name.
            file_path = chunk.metadata.get("source", "")          # original full path
            chunk.metadata["source"] = os.path.basename(file_path)

        # Creating Embeddings
        # Example using OllamaEmbeddings: All You'll need is to install Ollama and run it with the model you want to use.
        embeddings = OllamaEmbeddings(model=config["ollama_model"]) #Change the model name if needed.

        # 4. Store Embeddings in ChromaDB
        logger.info(f"Store Embeddings in local DB, path: {config['db_path']}, please wait...")
        chroma_client = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=config["db_path"]
        )
        logger.info("Data Processing finished successfully")
        return chroma_client

# Testing the embeddings
if __name__ == "__main__":
    asyncio.run(chroma_client:=__DataProcessing().Processing())
    for i, doc in enumerate(chroma_client.get_all_documents()[:5]):   # just first 5
        logger.debug(f"Chunk {i} | Source: {doc.metadata.get('source')}")
    print("Data processing complete.  Embeddings stored in ChromaDB.")