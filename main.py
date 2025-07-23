from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="Briefly - Legal Document Analyzer")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Thread pool for running long tasks
executor = ThreadPoolExecutor(max_workers=1)

@app.get("/")
async def root():
    return {"message": "Briefly API is running"}

@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files to the data directory"""
    try:
        uploaded_files = []
        
        for file in files:
            # Check if file is PDF
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            # Save file to data directory
            file_path = DATA_DIR / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append(file.filename)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Successfully uploaded {len(uploaded_files)} files",
                "files": uploaded_files
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    """List all PDF files in the data directory"""
    try:
        pdf_files = [f.name for f in DATA_DIR.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
        return {"files": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific file from the data directory"""
    try:
        file_path = DATA_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return {"message": f"File {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_create_database():
    """Run the create_database.py script"""
    try:
        result = subprocess.run([sys.executable, "create_database.py"], 
                              capture_output=True, text=True, check=True)
        return {"success": True, "output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": e.stdout, "error": e.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def run_query_data():
    """Run the query_data.py script"""
    try:
        result = subprocess.run([sys.executable, "query_data.py"], 
                              capture_output=True, text=True, check=True)
        return {"success": True, "output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": e.stdout, "error": e.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

@app.post("/create-database")
async def create_database():
    """Create/update the vector database from uploaded PDFs"""
    try:
        # Check if there are any PDF files
        pdf_files = [f for f in DATA_DIR.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
        if not pdf_files:
            raise HTTPException(status_code=400, detail="No PDF files found. Please upload files first.")
        
        # Run create_database.py in background
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_create_database)
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Database created/updated successfully",
                    "output": result["output"]
                }
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Error creating database: {result['error']}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-documents")
async def analyze_documents():
    """Run the document analysis and return results"""
    try:
        # Check if database exists
        if not Path("chroma_db").exists():
            raise HTTPException(
                status_code=400, 
                detail="Database not found. Please create database first."
            )
        
        # Run query_data.py in background
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_query_data)
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Document analysis completed successfully",
                    "output": result["output"],
                    "analysis_results": parse_analysis_output(result["output"])
                }
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Error analyzing documents: {result['error']}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def parse_analysis_output(output: str) -> dict:
    """Parse the output from query_data.py into structured data"""
    try:
        results = {}
        current_field = None
        current_content = []
        
        lines = output.split('\n')
        for line in lines:
            if ' : ' in line and not line.startswith('    '):
                # Save previous field if exists
                if current_field:
                    results[current_field] = '\n'.join(current_content).strip()
                
                # Start new field
                parts = line.split(' : ', 1)
                current_field = parts[0].strip()
                current_content = [parts[1]] if len(parts) > 1 else []
            elif current_field and line.strip():
                current_content.append(line)
        
        # Save last field
        if current_field:
            results[current_field] = '\n'.join(current_content).strip()
        
        return results
    except Exception:
        return {"raw_output": output}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_dir_exists": DATA_DIR.exists(),
        "database_exists": Path("chroma_db").exists()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)