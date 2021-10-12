from sys import path
from functools import lru_cache

from pydantic import BaseSettings

__all__ = ["get_settings"]


SRC_PATH = path[2]


class Settings(BaseSettings):
    secret_key: str

    qwhale_token: str

    redis_host: str
    redis_port: int

    auth_jwt_algorithms = ["HS256"]

    class Config:
        env_file = f"{SRC_PATH}/.env"
        fields = {
            'secret_key': {
                'env': 'secret_key',
            },
            'qwhale_token': {
                'env': "qwhale_token"
            },
            'redis_port': {
                'env': "redis_port"
            },
            'redis_host': {
                'env': "redis_host"
            },
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
