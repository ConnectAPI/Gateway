from pathlib import Path
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_url: str

    super_user_secret: str
    secret_key: str

    jwt_algorithms = ["HS256"]
    jwt_lifetime = 1200  # 20 minuets

    super_user_scope = "super_user"
    allowed_scopes = [
        "token:create", "token:delete", "token:read",
        "service:create", "service:read", "service:delete", "service:write",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
