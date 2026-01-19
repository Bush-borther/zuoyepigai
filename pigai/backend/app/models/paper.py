from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    image_path = Column(String)
    aligned_image_path = Column(String, nullable=True) # New field
    status = Column(String, default="pending") # pending, graded, failed
    total_score = Column(Float, default=0.0)
    results = Column(JSON, default=[]) # List of {region_id, ocr_text, is_correct, score}
    created_at = Column(String, nullable=True)

    template = relationship("Template")
