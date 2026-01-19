from pydantic import BaseModel
from typing import List, Optional, Any

class GradingResult(BaseModel):
    region_id: str
    ocr_text: str
    is_correct: bool
    score: float
    feedback: Optional[str] = None

class PaperBase(BaseModel):
    template_id: int

class PaperCreate(PaperBase):
    pass

class Paper(PaperBase):
    id: int
    image_path: str
    aligned_image_path: Optional[str] = None
    status: str
    total_score: float
    results: List[GradingResult] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
