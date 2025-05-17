import os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

# Create router
router = APIRouter(
    prefix="/api/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
)

# Define path for uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), session_id: Optional[str] = None):
    """
    Upload a file (CSV, Excel) to be analyzed.
    Returns metadata about the uploaded file.
    """
    # Check for valid file extension
    valid_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported types: {', '.join(valid_extensions)}"
        )
    
    # Define unique filename using session_id if provided
    if session_id:
        dest_path = os.path.join(UPLOAD_DIR, f"{session_id}{file_ext}")
    else:
        # Use original filename if no session_id
        dest_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save the file
        with open(dest_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Get file metadata
        file_info = {"filename": file.filename, "size_bytes": os.path.getsize(dest_path)}
        
        # Load into pandas to extract schema information
        if file_ext == '.csv':
            df = pd.read_csv(dest_path)
        else:  # Excel
            df = pd.read_excel(dest_path)
        
        # Extract schema info
        columns_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            columns_info.append({
                "name": col,
                "type": dtype,
                "sample": str(sample) if sample is not None else None
            })
        
        # Get basic stats
        file_info["rows"] = len(df)
        file_info["columns"] = len(df.columns)
        file_info["schema"] = columns_info
        
        # Add path information for internal use
        file_info["path"] = dest_path
        
        return {
            "success": True,
            "message": f"File uploaded successfully: {file.filename}",
            "file_info": file_info
        }
        
    except Exception as e:
        # Clean up file if it was partially written
        if os.path.exists(dest_path):
            os.remove(dest_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        ) 