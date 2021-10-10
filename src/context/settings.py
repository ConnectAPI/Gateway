from functools import lru_cache
from datetime import timedelta

from pydantic import BaseSettings

__all__ = ["get_settings"]


class Settings(BaseSettings):
    secret_key: str
    session_max_age: int

    allow_session_over_http: bool

    qwhale_token: str

    redis_host: str
    redis_port: int

    auth_jwt_algorithms = ["HS256"]
    auth_jwt_lifespan = timedelta(hours=24)

    class Config:
        env_file = ".env"
        fields = {
            'secret_key': {
                'env': 'secret_key',
            },
            'session_max_age': {
                'env': 'session_max_age',
            },
            'allow_session_over_http': {
                'env': "allow_session_over_http"
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
