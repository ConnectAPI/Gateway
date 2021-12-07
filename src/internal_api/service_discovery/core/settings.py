from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings


ENV_FILE_PATH = str(Path(__file__).parent.parent / '.env')


class Settings(BaseSettings):
    secret_key: str
    mongo_url: str

    jwt_algorithms: list = ["HS256"]

    debug = True

    docker_network_name: str = "connectapi_core"

    class Config:
        env_file: str = ENV_FILE_PATH
        fields = {
            'mongo_url': {
                'env': 'mongo_url',
            },
            'secret_key': {
                'env': 'secret_key',
            },
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
