# Briefly 
A RAG Workflow custom built for paralegals and legal professionals to automate legal document analysis. <br/><br/>

Briefly is a comprehensive application that combines modern web technologies with local AI models to provide secure, efficient analysis of legal documents. Upload PDF files, process them through AI embeddings, and get structured analysis results for key legal information.

<img width="2102" height="1223" alt="Image" src="https://github.com/user-attachments/assets/17b1d4af-a71a-43ca-a55b-3ab72069758c" />

## Features 
- Local LLM processing using Ollama for <b>absolute privacy</b>
- ChromaDB vector database integration for efficient <b>document search and retrieval</b>
- <b>Organized</b> analysis results for key legal fields 
- Complete <b>containterization</b> of application using Docker
- Upload <b>multiple</b> PDF documents simultaneously
- No external APIs and <b>no data sent</b> to external services
- <b>Automatic cleanup</b> with files cleared on application restart

## RAG Workflow Schema
<img width="1252" height="330" alt="Image" src="https://github.com/user-attachments/assets/fbd26367-dda7-4b77-8817-8858d34e4aa0" />

<img width="965" height="688" alt="Image" src="https://github.com/user-attachments/assets/c89e9105-fc59-447b-aeba-52b4fea75dfe" />

## Tech Stack
Frontend
- Next.js + TypeScript for type safety and frontend framework
- Tailwind CSS for modern, responsive styling

Backend
- FastAPI for high-performance API endpoints
- ChromaDB for vector database, semantic search, and document embeddings
- LangChain for document processing and text splitting
- PyPDF for document text extraction

AI/ML Stack
- Ollama for running LLMs locally, yielding secure queries, and protecting sensitive document information 
- LLaMA2:7b model for document analysis
- all-minilm model for vector embeddings

## System Requirements
- Docker and Docker Compose
- 16GB+ RAM <b>highly</b> recommended for AI models (Document analysis using llama2:7b will take a significant amount of time with minimum hardware requirements)
- 5GB+ storage for models and documents

## Installation & Setup
1. Clone the Repository
```
git clone <repository-url>
cd briefly
```

2.  Build and start all services
```
docker-compose up --build
```

3. Download AI Models (One-time only)

```
docker exec briefly-ollama ollama pull all-minilm
docker exec briefly-ollama ollama pull llama2:7b
```

4. Navigate to the application
```
http://localhost:3000
```


## Usage
1. Upload Documents 
- Click "Upload Files" and select PDF documents 
- Multiple files can be uploaded simultaneously 

2. Process Documents
- Click "Process Documents" to generate vector embeddings 
- This extracts text and creates searchable chunks 
- Wait for processing to complete 
- NOTE: If you forgot to upload a document that you want analyzed and you already hit "Process Documents", all you need to do is hit "Process Documents" again after you've added the document. If you forget to hit "Process Documents" after you added your new document, the analysis will be done on the previously processed documents and will exclude the new document added entirely.

3. Analyze Documents
- Click "Analyze Documents" to run AI analysis 
- The system prompts models based on a preset list of queries the documents for key legal information
- With multiple documents to carefully index and parse, results will take several minutes to load
- Results are displayed in structured format

4. Review Results
- The analysis provides structured information for:

- Plaintiff: Name identification
- DOB: Date of birth extraction
- SSN: Social security number (when legally appropriate)
- DOI: Date of incident
- Insurance: Insurance company information
- Incident Overview: Summary of the incident
- Treatment Overview: Medical treatment details
- Past Medical History: Relevant medical background
- Social History: Witness accounts and social factors
- Earnings: Financial information
- Billing: Medical billing details
- Medical Records: Detailed medical record entries

## Docker Services

services
- ollama:      # AI model server (Port 11434)
- backend:     # FastAPI server (Port 8000)  
- frontend:    # Next.js app (Port 3000)
  
Data Persistence
- ollama_data: Stores downloaded AI models
- ./data: PDF upload directory
- ./chroma_db: Vector database storage 



