import os
import json
import asyncio
import pathlib
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
        for chunk in chunks:
            # If you loaded the PDF via DirectoryLoader, the metadata already contains
            # "source": "path/to/file.pdf".  We'll override it with just the file name.
            file_path = chunk.metadata.get("source", "")          # original full path
            chunk.metadata["source"] = os.path.basename(file_path)

        if config.get("store_chunks", False):
            # Decide whether to store chunks as Plain-Text version for debugging purposes !!
            output_dir   = pathlib.Path(config.get("output_path", "output"))
            output_file  = output_dir / "chunks.txt"

            # make sure the directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
    
            # Open the file & write every chunk
            try:
                with open(output_file, "w", encoding="utf-8") as fp:
                    for i, chunk in enumerate(chunks, start=1):
                        # Every Document from LangChain has a `page_content` attribute that holds the text.
                        # If you also want the metadata (file name, page number, …) add it too.
                        fp.write(f"--- CHUNK {i} ---\n")
                        fp.write(chunk.page_content)
                        fp.write("\n\n")
                        # Optional: write metadata on a separate line (JSON‑serialisable)
                        if chunk.metadata:
                            fp.write(f"Metadata: {json.dumps(chunk.metadata, ensure_ascii=False)}\n\n")

                logger.info(f"Successfully written {len(chunks)} chunks to {output_file}")
            except IOError as e:
                logger.warning(f"An Error occured while writing chunks to file, error details: {str(e)}")
            except Exception as e:
                logger.warning(f"An exception occured while writing chunks to file, more details: {str(e)}")


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
    print("Test Data processing complete.  Embeddings stored in ChromaDB.")