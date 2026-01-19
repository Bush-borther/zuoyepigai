from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image_path = Column(String)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    regions = Column(JSON, default=[]) # List of regions: {id, x, y, w, h, type, score...}
    created_at = Column(String, nullable=True) # ISO format date
