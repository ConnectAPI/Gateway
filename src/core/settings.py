from sys import path
from functools import lru_cache

from pydantic import BaseSettings

__all__ = ["get_settings"]


class Settings(BaseSettings):
    secret_key: str

    mongo_url: str

    redis_host: str
    redis_port: int

    env: str
    auth_jwt_algorithms = ["HS256"]

    host: str = "0.0.0.0"
    port: int = 80


@lru_cache
def get_settings() -> Settings:
    return Settings()
