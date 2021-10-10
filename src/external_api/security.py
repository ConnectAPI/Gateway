from datetime import datetime

import jwt
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from context import get_settings


__all__ = ["OAuthJWTBearer", "auth_flow"]


class OAuthJWTBearer(OAuth2PasswordBearer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret = get_settings().secret_key

    def generate_jwt(
            self,
            user_id,
            tuid: str,
            scopes: list = None,
    ):
        if scopes is None:
            scopes = []
        encoded = jwt.encode(
            {
                "exp": (datetime.now() + get_settings().auth_jwt_lifespan).timestamp(),
                "nbf": datetime.now().timestamp(),
                "iss": "qwahle",
                "iat": datetime.now().timestamp(),
                "sub": user_id,
                "scopes": scopes,
                "tuid": tuid
            },
            self.secret,
            algorithm=get_settings().auth_jwt_algorithms[0]
        )
        return encoded

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

auth_flow = OAuthJWTBearer(tokenUrl="auth/token")
