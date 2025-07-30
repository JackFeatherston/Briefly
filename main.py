from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

app = FastAPI(title="Briefly")

# Configuring CORS to let frontend (port 3000) and backend (port 8000) talk
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory paths
DATA_DIR = Path("data")
CHROMA_PATH = Path("chroma_db")

DATA_DIR.mkdir(exist_ok=True)



# Clear database and data on startup
def clear_on_startup():
    """
        Removes all previously existing files from /data and /chroma_db.
        Makes sure that the user doesn't analyze unrelated leftover documents from previous sessions.
    """
    try:
        # Clear /chroma_db
        if CHROMA_PATH.exists():
            shutil.rmtree(CHROMA_PATH, ignore_errors=True)
            
        # Clear uploaded files in /data
        for file in DATA_DIR.glob("*.pdf"):
            try:
                file.unlink()
            except:
                pass
    except Exception as e:
        print(f"Cleanup warning: {e}")
            
        

clear_on_startup()


@app.get("/")
async def root():
    return {"message": "Briefly API is running"}


@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    """
        Accepts list of PDF files, validates them, and adds to /data to be processed.
        Returns upload status and list of uploaded filenames
    """
    try:
        uploaded_files = []
        
        for file in files:
            # Check if file is PDF
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not a PDF"
                )
            
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
    """
        Get a list all the PDF files inside of /data.
    """
    try:
        pdf_files = [
            file.name for file in DATA_DIR.iterdir() 
            if file.is_file() and file.suffix.lower() == '.pdf'
        ]
        return {"files": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """
        Delete a specific file from /data.
        Takes in a filename as a string.
        Returns status message on deletion
    """
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
    """
        Runs the create_database.py script as a subprocess to build the vector database.
        Returns status message.
    """
    try:
        result = subprocess.run(
            [sys.executable, "create_database.py"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return {"success": True, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def run_query_data():
    """
        Runs the query_data.py script as a subprocess to get llm responses.
        Returns status message.
    """
    try:
        result = subprocess.run(
            [sys.executable, "query_data.py"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return {"success": True, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


@app.post("/create-database")
async def create_database():
    """
        Create/update the vector database from uploaded PDFs.
        Processes all uploaded PDFS, extracts text context, and stores
        vector embeddings into vector database (/chroma_db).
        Returns status message.
    """
    try:
        # Check if there are any PDF files
        pdf_files = [
            file for file in DATA_DIR.iterdir()
            if file.is_file() and file.suffix.lower() == '.pdf'
        ]
        if not pdf_files:
            raise HTTPException(status_code=400, detail="No PDF files found. Please upload files first.")
        
        # Run create_database.py script
        result = run_create_database()
        
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
    """
        Query llm with prompts and analyze processed documents.
        Returns response to each prompt in a nice format.
    """
    try:
        # Check if database exists
        if not Path("chroma_db").exists():
            raise HTTPException(
                status_code=400, 
                detail="Database not found. Please create database first."
            )
        
        # Run query_data.py script
        result = run_query_data()
        
        if result["success"]:
            # Parse raw llm output into structured format
            analysis_results = parse_analysis_output(result["output"])

            return JSONResponse(
                status_code=200,
                content={
                    "message": "Document analysis completed successfully",
                    "output": result["output"],
                    "analysis_results": analysis_results
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
    """
        Parse the output from query_data.py into structured data.
        Takes in string output from the llm response to the multiple queries.
        Returns dictionary with field names and analysis as key and values
    """
    try:
        results = {}
        current_field = None
        current_content = []
        
        lines = output.split('\n')
        for line in lines:
            # Check if this line starts a new field
            if ' : ' in line and not line.startswith('    '):
                # Save previous field if exists
                if current_field:
                    results[current_field] = '\n'.join(current_content).strip()
                
                # Preocces the new field
                parts = line.split(' : ', 1)
                current_field = parts[0].strip()
                current_content = [parts[1]] if len(parts) > 1 else []

            # If its not a new field, just keep adding to the current field we're scanning
            elif current_field and line.strip():
                current_content.append(line)
        
        # Save last field
        if current_field:
            results[current_field] = '\n'.join(current_content).strip()
        
        return results
    except Exception:
        return {"raw_output": output}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)