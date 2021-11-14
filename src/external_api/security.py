import jwt
from fastapi import HTTPException, status, Request
from fastapi.security import APIKeyHeader

from context import get_settings


__all__ = ["JWTBearer", "auth_flow"]


class JWTBearer(APIKeyHeader):
    def __init__(self, *args, **kwargs):
        super().__init__(name="access-token", description="Authentication JWT key for services", *args, **kwargs)
        self.secret = get_settings().secret_key

    async def __call__(self, request: Request, required_scopes: list = None):
        if required_scopes is None:
            required_scopes = []
        token = await super().__call__(request)
        try:
            json_token = jwt.decode(token, self.secret, algorithms=get_settings().auth_jwt_algorithms)
            for scope in required_scopes:
                if scope not in json_token["scopes"]:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Do not have permission for scope '{scope}'"
                    )
            return json_token
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

auth_flow = JWTBearer()
