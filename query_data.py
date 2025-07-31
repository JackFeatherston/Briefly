import chromadb
import os
import ollama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"


def main():
    query_rag()


def query_rag():

    # Preparing database with vector embeddings
    embedding_function = get_embedding_function()
    vector_store = Chroma(
        collection_name="documents",
        persist_directory=CHROMA_PATH, 
        embedding_function=embedding_function
    )

    queries = {
        "Plaintiff" : "What is the Plaintiffs first and last name. Example format: Jane Smith. Say nothing else except for the name or Unknown",
        "DOB" : "What is the Plaintiff's Date of Birth. Example format:  06 / 12 / 1999. Say nothing else except for the date of birth or Unknown",
        "SSN" : """What is the Plaintiff's Social Security Number. Reply with just the number only or say Unknown if you cannot legally answer.""",
        "DOI" : "What is the Date of Incident. Example format:  06 / 12 / 1999. Say nothing else except for the date of incident or Unknown.",
        "Insurance" : """What is the Plaintiff's Insurance Company. Write the Company Name and any other concise pieces of information.
                         Do not give any other reponse besides the previous stated bits of information.""",
        "Incident Overview" : """Write a brief three to four sentence summary describing the incident including the Plaintiffs name 
                                and the date, time, and location of the incident.""",
        "Treatment Overview" : """Write a detailed paragraph for each significant date that the Plaintiff underwent treatment. 
                                Include important facts and dates. Each paragraph should have its own header and be spaced apart from other paragraphs.""",
        "Past Medical History" : """Write a concise, three sentence paragraph describing the Plaintiff's past medical history. 
                            If there is no past medical history found then you may state that in one brief sentence.""",
        "Social History" : "Write a concise paragraph describing any eye witness accounts or any other details that relate outside people to the Plaintiff and incident",
        "Earnings" : "Write brief summaries of any deposits and bank statements",
        "Billing" : """Write the Sender of the Bill, Dates of Service, Description of Services,
                    Total Charges, Adjustments, Payments, and Balance. Do not give any other reponse besides the previous stated bits of information.""",
        "Medical Records" : "For each entry, write the Date, Facility, Summary, and which PDF and Label from the context provided you got the information from"
    }

    responses = {}

    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    client = ollama.Client(host=OLLAMA_BASE_URL)
    # client = ollama.Client()

    # change as needed 
    # model = "llama2:13b"
    model = "llama2:7b"

    for key, query_text in queries.items():

        # Searching database for relevant chunks
        relevant_chunks = vector_store.similarity_search_with_relevance_scores(query_text, k=5)

        context_chunks = []
        for doc, _score in relevant_chunks:
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
        If you don't know the answer, just say: Unknown.
        
        ----
        Here is the context to answer the question:
        {context_text}

        Question:
        {query_text}
        
        """

        # LLM response

        response = client.generate(model=model, prompt=BRIEFLY_PROMPT_TEMPLATE)
        responses[key] = response.response


    print("--------------")
    for field, response in responses.items():
        
        print(field + " : " + response)
        print()
        print()

        
    
def get_embedding_function():
    # embeddings =  OllamaEmbeddings(model="nomic-embed-text")
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL
    )
    return embeddings


if __name__ == "__main__":
    main()