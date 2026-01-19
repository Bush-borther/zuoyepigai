from typing import List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import cv2
from datetime import datetime

from app.core.database import get_db
from app.models import template as models
from app.schemas import template as schemas

router = APIRouter()

UPLOAD_DIR = "backend/data/templates"

@router.get("/", response_model=List[schemas.Template])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = db.query(models.Template).offset(skip).limit(limit).all()
    return templates

@router.post("/", response_model=schemas.Template)
def create_template(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Ensure directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get image dimensions
    img = cv2.imread(file_path)
    height, width, _ = img.shape
    
    # Save relative path for frontend access
    # Frontend will access via /static/templates/{filename}
    db_template = models.Template(
        name=name,
        image_path=f"templates/{filename}",
        width=width,
        height=height,
        created_at=datetime.now().isoformat()
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/{template_id}", response_model=schemas.Template)
def read_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template

@router.put("/{template_id}", response_model=schemas.Template)
def update_template(
    template_id: int,
    template_in: schemas.TemplateUpdate,
    db: Session = Depends(get_db)
):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template_in.name is not None:
        db_template.name = template_in.name
    if template_in.regions is not None:
        # Pydantic v2 dump/dict
        db_template.regions = [region.model_dump() for region in template_in.regions]
        
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Should delete file too
    try:
        full_path = os.path.join("backend/data", db_template.image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    db.delete(db_template)
    db.commit()
    return {"ok": True}
