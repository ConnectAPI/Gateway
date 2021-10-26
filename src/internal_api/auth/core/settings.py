from pathlib import Path
from functools import lru_cache

from pydantic import BaseSettings

ENV_FILE_PATH = str(Path(__file__).parent.parent / '.env')


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

    class Config:
        env_file: str = ENV_FILE_PATH
        fields = {
            'mongo_url': {
                'env': 'mongo_url',
            },
            'super_user_secret': {
                'env': 'super_user_secret',
            },
            'secret_key': {
                'env': 'secret_key',
            }
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
