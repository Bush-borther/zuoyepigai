from sqlalchemy.orm import Session
from app.models import paper as paper_models
from app.models import template as template_models
from app.services.image_service import image_service
from app.services.ocr_service import ocr_service
import os
import cv2

class GradingService:
    def grade_paper(self, paper_id: int, db: Session):
        paper = db.query(paper_models.Paper).filter(paper_models.Paper.id == paper_id).first()
        if not paper:
            raise ValueError("Paper not found")
        
        template = db.query(template_models.Template).filter(template_models.Template.id == paper.template_id).first()
        if not template:
            raise ValueError("Template not found")

        try:
            # Paths
            # Assuming paths are relative to backend/data or project root?
            # In models we stored "templates/xxx.jpg", static mount is "backend/data".
            # Real file path is "backend/data/templates/xxx.jpg"
            
            base_path = "backend/data"
            template_path = os.path.join(base_path, template.image_path)
            paper_path = os.path.join(base_path, paper.image_path)
            
            # 1. Align
            aligned_img = image_service.align_image(template_path, paper_path)
            
            # Save aligned image for debug/report (optional)
            aligned_path = paper_path.replace(".jpg", "_aligned.jpg").replace(".png", "_aligned.png")
             # Determine extension if replacement failed (e.g. funny filename)
            if "_aligned" not in aligned_path:
                 root, ext = os.path.splitext(paper_path)
                 aligned_path = f"{root}_aligned{ext}"

            cv2.imwrite(aligned_path, aligned_img)
            
            results = []
            total_score = 0
            
            # 2. Iterate regions
            for region in template.regions:
                # region is a dict from JSON column
                r_id = region.get('id')
                x = int(region.get('x'))
                y = int(region.get('y'))
                w = int(region.get('width'))
                h = int(region.get('height'))
                r_type = region.get('type')
                metadata = region.get('metadata', {})
                
                # Crop
                # Ensure coordinates are within image
                # TODO: add bounds check
                cropped = image_service.crop_region(aligned_img, x, y, w, h)
                
                # 3. OCR (if answer area)
                ocr_text = ""
                is_correct = False
                score = 0.0
                feedback = ""
                
                if r_type == 'answer_area':
                    ocr_text = ocr_service.recognize_text(cropped)
                    std_answer = metadata.get('answer', '')
                    
                    # Simple comparison logic (Exact match)
                    # TODO: Add fuzzy match or AI semantic match
                    if std_answer and ocr_text.strip() == std_answer.strip():
                        is_correct = True
                        score = 1.0 # Default score per question? Need score in metadata
                    else:
                        is_correct = False
                
                # Store result
                results.append({
                    "region_id": r_id,
                    "ocr_text": ocr_text,
                    "is_correct": is_correct,
                    "score": score,
                    "feedback": f"Expected: {metadata.get('answer')}, Got: {ocr_text}"
                })
                total_score += score
            
            # Update Paper
            paper.status = "graded"
            paper.results = results
            paper.total_score = total_score
            # Store relative path
            if "backend/data/" in aligned_path:
                paper.aligned_image_path = aligned_path.split("backend/data/")[1]
            else:
                 # Fallback
                 paper.aligned_image_path = paper.image_path
            
            db.commit()
            
        except Exception as e:
            print(f"Grading failed: {e}")
            paper.status = "failed"
            db.commit()
            raise e

grading_service = GradingService()
