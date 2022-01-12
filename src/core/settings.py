from functools import lru_cache

from pydantic import BaseSettings, Field

__all__ = ["get_settings"]


class Settings(BaseSettings):
    # gateway
    secret_key: str = "fooasddfsa"
    mongo_url: str = "mongodb://gatewayname:gatewaypass@5.183.9.78:27017/gateway"
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    env: str = "dev"
    host: str = "127.0.0.1"
    port: int = 8080

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

    class Config:
        case_sensitive = False
        fields = {
            "secret_key": {"env": "secret_key"},
            "mongo_url": {"env": "mongo_url"},
            "redis_host": {"env": "redis_host"},
            "env": {"env": "env"},
            "host": {"env": "host"},
            "port": {"env": "port"},
            "auth_token_header": {"env": "auth_token_header"},
            "super_user_secret": {"env": "super_user_secret"},
            "jwt_algorithms": {"env": "jwt_algorithms"},
            "jwt_lifetime": {"env": "jwt_lifetime"},
            "super_user_scope": {"env": "super_user_scope"},
            "docker_network_name": {"env": "docker_network_name"},
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
