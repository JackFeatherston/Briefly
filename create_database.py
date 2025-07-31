import chromadb
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
import shutil
import requests
import time

# Setting up db

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"


def main():

    # Make sure all ollama utilities are loaded in
    # wait_for_ollama()

    # Create (or update) the data store. 
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def wait_for_ollama():
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✓ Ollama is ready!")
                return True
        except Exception as e:
            print(f"Waiting for Ollama... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
    
    raise Exception("Ollama is not responding after maximum retries")


def load_documents():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    return documents


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        add_start_index=False,
    )
    return text_splitter.split_documents(documents)


def get_embedding_function():
    # embeddings =  OllamaEmbeddings(model="nomic-embed-text")
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL
    )
    return embeddings


def add_to_chroma(chunks: list[Document]):

    # Load the existing database
    vector_store = Chroma(
    collection_name="documents",
    embedding_function=get_embedding_function(),
    persist_directory=CHROMA_PATH,  # Where to save data locally
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = vector_store.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"---> Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        vector_store.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("---> No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


if __name__ == "__main__":
    main()
