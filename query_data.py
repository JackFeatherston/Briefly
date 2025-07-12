import chromadb
import os
import ollama
from dotenv import load_dotenv
from openai import OpenAI


from langchain_community.vectorstores import Chroma
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Load variables from .env into the environment
load_dotenv()

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"


def main():
    # Prepare the DB.
    embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    db = Chroma(
        collection_name="bee_movie",
        persist_directory=CHROMA_PATH, 
        embedding_function=embedding_function
    )

    # Searching the DB
    user_query =  input("What do you want to know about the Bee Movie?\n\n")
    results = db.similarity_search_with_relevance_scores(user_query, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    # Extracted from results

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    print(f"CONTEXT TEXT IS ---------- \n\n{context_text}")

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

    client = ollama.Client()

    model = "gemma3"

    response = client.generate(model=model, prompt=prompt)

    # LLM response

    print("Response from Ollama: ")
    print(response.response)


if __name__ == "__main__":
    main()