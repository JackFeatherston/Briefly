import chromadb
import os
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

    # Access the API key from environment variables
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    message = f"""
    You are a helpful assistant when in comes to answering questions about The Bee Movie. 
    You have been provided the entire script of the Bee Movie. 
    You answer questions about anything related to The Bee Movie, but you only answer based on knowledge I'm providing you. 
    You don't use your internal knowledge and you don't make things up.
    If you don't know the answer, just say: I don't know.

    ---------------------------------

    The data: 
    {context_text}
    """ 

    # Send request
    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct",
        messages = [
        {"role": "system", "content": message},
        {"role": "user", "content": user_query}
        ],
        # temperature=0.7,
        max_tokens=150
    )

    # Print result
    print("Assistant says:", response.choices[0].message.content)



if __name__ == "__main__":
    main()

# # Embedding function

# embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# collection = chroma_client.get_or_create_collection(
#     name="bee_movie",
#     embedding_function=embedding_fn
# )


# user_query =  input("What do you want to know about the Bee Movie?\n\n")

# results = collection.query(
#     query_texts=[user_query],
#     n_results=3
# )

# # Extracted from results

# retrieved_docs = "\n\n".join(doc for doc in results["documents"][0])

# # print(results["documents"])

# # Access the API key from environment variables
# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPENROUTER_API_KEY")
# )

# message = f"""
# You are a helpful assistant when in comes to answering questions about The Bee Movie. 
# You have been provided the entire script of the Bee Movie. 
# You answer questions about anything related to The Bee Movie, but you only answer based on knowledge I'm providing you. 
# You don't use your internal knowledge and you don't make things up.
# If you don't know the answer, just say: I don't know.

# ---------------------------------

# The data: 
# {retrieved_docs}
# """ 

# # Send request
# response = client.chat.completions.create(
#     model="meta-llama/llama-3.3-70b-instruct",
#     messages = [
#     {"role": "system", "content": message},
#     {"role": "user", "content": user_query}
#     ],
#     # temperature=0.7,
#     max_tokens=150
# )

# # Print result
# print("Assistant says:", response.choices[0].message.content)
