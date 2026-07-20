from functools import lru_cache

from langchain_openrouter import ChatOpenRouter

from app.core.config import settings


@lru_cache(maxsize=4)
def get_llm(temperature: float = 0.2) -> ChatOpenRouter:
    settings.validate()
    return ChatOpenRouter(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        temperature=temperature,
    )
