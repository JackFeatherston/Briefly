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

    context_chunks = []
    for doc, _score in results:
        chunk_id = doc.metadata.get("id", "unknown-id")
        chunk_content = doc.page_content
        context_chunks.append(f"[ID: {chunk_id}]\n{chunk_content}")

    context_text = "\n\n---\n\n".join(context_chunks)


    BRIEFLY_PROMPT_TEMPLATE = f"""
    You are a senior paralegal with twenty years of experience working for respectable, corporate law firms.
    You currently represent a law firm that provides defense for companies who are experiencing lawsuits against them.
    Your main job is to summarize crucial details regarding courtcases. 
    The details include important dates, facts, any statements that may contradict each other, and anything else that you may deem important to be reported.
    Your writing style should be concise, informative, and objective at all times. 
    You only answer based on the documents you are provided. 
    You don't use your internal knowledge and you don't make things up.
    If you don't know the answer, just say: I don't know.
    Here is the following format to which you must stricly adhere to: 
    
    ----
    Plaintiff: [Plaintiff Name Here]
    DOB: [Plaintiff Date of Birth Here]
    SSN: [Plaintiff Social Security Number Here]
    DOI: [Date of Incident Here]

    Insurance: [Plaintiff Insurance Here]

    Incident Overview: [Brief Three to Four sentence summary describing the incident including the Plaintiff's name, 
    and location, date, and time of incident]

    Treatment Overview: [Include a detailed paragraph for each significant date that the Plaintiff underwent treatment. Include important facts and dates]


    Little summaries of documents: []


    ----
    Here are your documents to summarize:
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
    print(f"\n\n---\nHere is context used to derive this answer ---------- \n\n{context_text}")
    print(response.response)
    return response.response
    


def get_embedding_function():
    embeddings =  OllamaEmbeddings(model="nomic-embed-text")
    return embeddings


if __name__ == "__main__":
    main()