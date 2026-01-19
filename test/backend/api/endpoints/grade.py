from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from backend.service.grading_service import grading_service

router = APIRouter()

class GradeRequest(BaseModel):
    filename: str

@router.post("/grade")
async def grade_exam_endpoint(request: GradeRequest):
    """
    Trigger grading for an uploaded file.
    """
    file_path = Path("backend/static/uploads") / request.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        result = grading_service.grade_exam(file_path)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
