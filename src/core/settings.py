from functools import lru_cache

from pydantic import BaseSettings

__all__ = ["get_settings"]


class Settings(BaseSettings):
    # gateway
    secret_key: str = "fooasddfsa"
    mongo_url: str = "mongodb://gatewayname:gatewaypass@5.183.9.78:27017/gateway"
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 80

    # auth
    auth_token_header: str = "x-access-token"
    super_user_secret: str = "usyusyauall"
    jwt_algorithms = ["HS256"]
    jwt_lifetime = 1200  # 20 minuets
    super_user_scope = "super_user"
    allowed_scopes = [
        "token:create", "token:delete", "token:read",
        "service:create", "service:read", "service:delete", "service:write",
    ]

    # service discovery
    docker_network_name: str = "connectapi"


@lru_cache
def get_settings() -> Settings:
    return Settings()
