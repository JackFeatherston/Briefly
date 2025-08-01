Briefly 
Next-generation AI-powered legal document analysis platform for paralegals and legal professionals.

Briefly is a comprehensive application that combines modern web technologies with local AI models to provide secure, efficient analysis of legal documents. Upload PDF files, process them through AI embeddings, and get structured analysis results for key legal information.

# Features
Secure PDF Upload: Upload multiple PDF documents simultaneously
AI-Powered Analysis: Local LLM processing using Ollama for enhanced privacy
Vector Database: ChromaDB integration for efficient document search and retrieval
Structured Output: Organized analysis results for key legal fields
Modern UI: Sleek, responsive Next.js frontend with Tailwind CSS
Containerized: Complete Docker setup for easy deployment
Real-time Processing: Live updates on document processing status
Local Processing: All AI analysis happens locally
No External APIs: No data sent to external services
File Isolation: Uploaded files are containerized
Automatic Cleanup: Files cleared on application restart

# Tech Stack
Frontend
Next.js + TypeScript for type safety and frontend framework
Tailwind CSS for modern, responsive styling

Backend
FastAPI for high-performance API endpoints
ChromaDB vector database for document embeddings
LangChain for document processing and text splitting
PyPDF for document text extraction

AI/ML Stack
Ollama for running LLMs locally for secure queries, protecting sensitive document information 
Gemma3 and LLaMA2 models for document analysis
all-minilm embeddings for vector search

# System Requirements
Docker and Docker Compose
8GB+ RAM recommended for AI models
5GB+ storage for models and documents

# Installation & Setup
1. Clone the Repository
```
git clone <repository-url>
cd briefly
```

2. First Time Setup

# Build and start all services
```
docker-compose up --build
```

3. Download AI Models (One-time only)

# Download embedding model
```
docker exec briefly-ollama ollama pull all-minilm
```

# Download analysis model
```
docker exec briefly-ollama ollama pull gemma3
```

4. Access the Application
Frontend: http://localhost:3000
Backend API: http://localhost:8000
Ollama: http://localhost:11434

# Usage
1. Upload Documents
Navigate to http://localhost:3000
Click "Upload Files" and select PDF documents
Supported format: PDF only
Multiple files can be uploaded simultaneously
2. Process Documents
Click "Process Documents" to create vector embeddings
This extracts text and creates searchable chunks
Wait for processing to complete
3. Analyze Documents
Click "Analyze Documents" to run AI analysis
The system queries the documents for key legal information
Results are displayed in structured format
4. Review Results
The analysis provides structured information for:

Plaintiff: Name identification
DOB: Date of birth extraction
SSN: Social security number (when legally appropriate)
DOI: Date of incident
Insurance: Insurance company information
Incident Overview: Summary of the incident
Treatment Overview: Medical treatment details
Past Medical History: Relevant medical background
Social History: Witness accounts and social factors
Earnings: Financial information
Billing: Medical billing details
Medical Records: Detailed medical record entries

# Docker Services
Services Overview
yaml
services:
  ollama:      # AI model server (Port 11434)
  backend:     # FastAPI server (Port 8000)  
  frontend:    # Next.js app (Port 3000)
Data Persistence
ollama_data: Stores downloaded AI models
./data: PDF upload directory
./chroma_db: Vector database storage 
