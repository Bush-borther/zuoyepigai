from fastapi import APIRouter
from backend.api.endpoints import upload, grade, config

api_router = APIRouter()

@api_router.get("/health")
def health_check():
    return {"status": "ok"}

# 注册各个端点（不添加 prefix，因为端点内部已经定义了路径）
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(grade.router, tags=["grade"])
api_router.include_router(config.router, tags=["config"])

# Export for backwards compatibility
router = api_router
