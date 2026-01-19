from fastapi import APIRouter
from app.api.endpoints import templates, papers

api_router = APIRouter()
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
