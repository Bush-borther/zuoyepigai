from typing import List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models import paper as models
from app.schemas import paper as schemas
from app.services.grading_service import grading_service

router = APIRouter()

UPLOAD_DIR = "backend/data/papers"

@router.get("/", response_model=List[schemas.Paper])
def read_papers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Paper).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Paper)
def upload_paper(
    template_id: int = Form(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_paper = models.Paper(
        template_id=template_id,
        image_path=f"papers/{filename}",
        status="pending",
        created_at=datetime.now().isoformat()
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    
    # Auto grade in background
    background_tasks.add_task(grading_service.grade_paper, db_paper.id, db)
    
    return db_paper

@router.get("/{paper_id}", response_model=schemas.Paper)
def read_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@router.post("/{paper_id}/grade", response_model=schemas.Paper)
def grade_paper_manual(paper_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    background_tasks.add_task(grading_service.grade_paper, paper_id, db)
    paper.status = "grading_queued"
    db.commit()
    return paper

from fastapi.responses import FileResponse
from app.services.report_service import report_service
from app.models import template as template_models

@router.get("/{paper_id}/report")
def get_report(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    template = db.query(template_models.Template).filter(template_models.Template.id == paper.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # Report path
    report_filename = f"report_{paper.id}.pdf"
    report_path = os.path.join(UPLOAD_DIR, report_filename)
    
    # Generate report (always regenerate for now to be safe)
    report_service.generate_report(paper, template, report_path)
    
    return FileResponse(report_path, media_type='application/pdf', filename=report_filename)
