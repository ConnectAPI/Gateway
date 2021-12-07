from sys import path
from functools import lru_cache

from pydantic import BaseSettings

__all__ = ["get_settings"]


SRC_PATH = path[2]


class Settings(BaseSettings):
    secret_key: str

    mongo_url: str

    redis_host: str
    redis_port: int

    env: str
    auth_jwt_algorithms = ["HS256"]

    host: str = "127.0.0.1"
    port: int = 80

    class Config:
        env_file = f"{SRC_PATH}/.env"
        fields = {
            'secret_key': {'env': 'secret_key'},
            'mongo_url': {'env': "mongo_url"},
            'redis_port': {'env': "redis_port"},
            'redis_host': {'env': "redis_host"},
            'env': {"env": "env"},
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
