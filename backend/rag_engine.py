import json
from logger.logger import Logger

from langchain.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


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

# 2️⃣ Create a retriever (gets 4 docs per query)
retriever = chroma.as_retriever(search_kwargs={"k": 8})

# ------------------------------------------------------------------
# 3️⃣ Prompt template (just the context + question)
# ------------------------------------------------------------------
prompt_template = """You are a helpful computer hardware expert assistant. You answer user questions about computer hardware based on the provided context documents.

Instructions:
- Use the provided context to answer questions about computer hardware, components, specifications, and technical details
- Be professional, accurate, and detailed in your responses
- If the context contains relevant information, provide a comprehensive answer
- If the context doesn't contain enough information, say "Based on the available information, I cannot provide a complete answer"
- Always cite the source documents when providing information

Context:
{context}

Question: {question}

Answer (include source file names in parentheses):
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# 4️⃣ LLM
llm = ChatOllama(model=config["ollama_model"], temperature=0)

# ------------------------------------------------------------------
# 5️⃣  Build the chain as a Runnable pipeline (answer + sources)
# ------------------------------------------------------------------
rag_chain_with_sources = (
    # Step 1 – the *only* input you give to the chain is the question
    RunnablePassthrough()                                         # <- input: question string

    # Step 2 – create a dict that contains the question **and** the
    #          list of documents that the retriever found
    | RunnableLambda(lambda q: {
        "question": q,
        "context": retriever.invoke(q)          # <-- list[Document] (updated method)
    })

    # Step 3 – feed the dict into the prompt template
    | prompt

    # Step 4 – run the LLM
    | llm

    # Step 5 – just grab the text from the LLM (no JSON, just a plain string)
    | StrOutputParser()
)

# 6️⃣ Helper that runs a question
def ask(question: str) -> tuple[str, list[str]]:
    """
    Returns the LLM answer **and** the list of sources that were used
    to build the context for that answer.
    """
    logger.info(f"Processing question: {question}")
    
    # 1️⃣  Grab the relevant documents once (so we can inspect them)
    docs = retriever.invoke(question)
    logger.info(f"Retrieved {len(docs)} documents for question")
    
    # Log document details for debugging
    for i, doc in enumerate(docs):
        logger.debug(f"Document {i+1}: Source={doc.metadata.get('source', 'Unknown')}, Length={len(doc.page_content)} chars")
        logger.debug(f"Content preview: {doc.page_content[:200]}...")

     # 2️⃣  Run the pipeline – it will internally *re‑run* the retriever,
    #      but we keep the documents we just fetched.
    answer = rag_chain_with_sources.invoke(question).strip()
    logger.info(f"Generated answer: {answer[:100]}...")

    # 3️⃣  Pull the 'source' metadata from each document
    sources = [doc.metadata.get("source", "") for doc in docs]
    logger.info(f"Sources used: {sources}")

    return answer, sources
