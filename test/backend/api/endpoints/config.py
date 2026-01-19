from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局配置存储（会话级别）
llm_config_store = {
    "api_key": None,
    "base_url": None,
    "model": None
}

class LLMConfig(BaseModel):
    api_key: str
    base_url: Optional[str] = "https://api.openai.com/v1"
    model: Optional[str] = "gpt-4o"

class LLMConfigStatus(BaseModel):
    configured: bool
    base_url: Optional[str] = None
    model: Optional[str] = None

@router.post("/llm")
async def update_llm_config(config: LLMConfig):
    """
    更新 LLM 配置
    """
    global llm_config_store
    
    llm_config_store["api_key"] = config.api_key
    llm_config_store["base_url"] = config.base_url
    llm_config_store["model"] = config.model
    
    logger.info(f"LLM config updated: base_url={config.base_url}, model={config.model}")
    
    # 更新 llm_client 的配置
    from backend.service.llm_client import llm_client
    llm_client.update_config(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model
    )
    
    return {
        "success": True,
        "message": "LLM 配置已更新"
    }

@router.get("/llm", response_model=LLMConfigStatus)
async def get_llm_config_status():
    """
    获取 LLM 配置状态（不返回 API Key）
    """
    global llm_config_store
    
    configured = llm_config_store["api_key"] is not None
    
    return LLMConfigStatus(
        configured=configured,
        base_url=llm_config_store["base_url"] if configured else None,
        model=llm_config_store["model"] if configured else None
    )
