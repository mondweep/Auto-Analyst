import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

# Create router
router = APIRouter(
    prefix="/exports",
    tags=["exports"],
    responses={404: {"description": "File not found"}},
)

# Get exports directory path
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")

@router.get("/{file_name}")
async def get_exported_file(file_name: str):
    """
    Serve exported data files for download
    """
    # Restrict to only known data files for security
    allowed_files = ['vehicles.csv', 'market_data.csv', 'automotive_analysis.csv']
    
    if file_name not in allowed_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = os.path.join(EXPORTS_DIR, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")
    
    return FileResponse(
        path=file_path, 
        filename=file_name,
        media_type='text/csv'
    ) 