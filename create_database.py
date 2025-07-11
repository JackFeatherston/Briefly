import chromadb
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os
import shutil

# Setting up db

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"


def main():
    generate_data_store


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(
        chunks, embedding_fn, persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()




# # Embedding function

# embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# collection = chroma_client.get_or_create_collection(
#     name="bee_movie",
#     embedding_function=embedding_fn
# )


# # loading documents

# loader = PyPDFDirectoryLoader(DATA_PATH)

# documents = loader.load()

# # splitting documents into chunks

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=300,
#     chunk_overlap=100,
#     length_function=len,
#     is_separator_regex=False
# )

# chunks = text_splitter.split_documents(documents)

# # initializing lists to be entered into chromadb

# documents = []
# metadata = []
# ids = []

# i = 0

# for chunk in chunks:
#     documents.append(chunk.page_content)
#     ids.append("ID"+str(i))
#     metadata.append(chunk.metadata)

#     i += 1

# # adding to chromadb

# collection.upsert(
#     documents=documents,
#     metadatas=metadata,
#     ids=ids
# )