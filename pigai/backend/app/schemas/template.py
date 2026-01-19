from pydantic import BaseModel
from typing import List, Optional, Any

class Region(BaseModel):
    id: str
    x: float
    y: float
    width: float
    height: float
    type: str # 'question_id', 'score_box', 'answer_area'
    metadata: Optional[Any] = {}

class TemplateBase(BaseModel):
    name: str

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    regions: Optional[List[Region]] = None

class Template(TemplateBase):
    id: int
    image_path: str
    width: Optional[int] = None
    height: Optional[int] = None
    regions: List[Region] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
