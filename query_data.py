import chromadb
import os
import argparse
import ollama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"


def main():

    # Create CLI for user query
    # parser = argparse.ArgumentParser()
    # parser.add_argument("query_text", type=str, help="The query text.")
    # args = parser.parse_args()
    # query_text = args.query_text

    # Get the user's query
    query_text = input("Ask a question! ")
    query_rag(query_text)


    # if len(results) == 0 or results[0][1] < 0.7:
    #     print(f"Unable to find matching results.")
    #     return


def query_rag(query_text: str):

    # Preparing database with vector embeddings
    embedding_function = get_embedding_function()
    vector_store = Chroma(
        collection_name="bee_movie",
        persist_directory=CHROMA_PATH, 
        embedding_function=embedding_function
    )

    # Searching database for relevant chunks
    results = vector_store.similarity_search_with_relevance_scores(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # print(f"CONTEXT TEXT IS ---------- \n\n{context_text}") testing a print output of the retrieved relevant chunks

    prompt = f"""
    You are a helpful assistant when in comes to answering questions about The Bee Movie. 
    You have been provided the entire script of the Bee Movie. 
    You answer questions about anything related to The Bee Movie, but you only answer based on knowledge I'm providing you. 
    You don't use your internal knowledge and you don't make things up.
    If you don't know the answer, just say: I don't know.

    ---------------------------------

    The data: 
    {context_text}
    """ 

    TEMPLATE = f"""
    Answer the question based only on the following context:
    {context_text}

    ---
    Answer the question based on the above context: {query_text}
    """

    client = ollama.Client()

    # change as needed 
    model = "gemma3"

    response = client.generate(model=model, prompt=TEMPLATE)

    # LLM response

    print("Response from Ollama: ")
    print(response.response)
    print(f"\n\n---\nHere is context used to derive this answer ---------- \n\n{context_text}")
    return response.response
    


def get_embedding_function():
    embeddings =  OllamaEmbeddings(model="nomic-embed-text")
    return embeddings


if __name__ == "__main__":
    main()