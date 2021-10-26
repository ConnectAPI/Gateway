import jwt
from fastapi import Header, HTTPException, status
from .core.settings import get_settings


def user_permissions(token: str = Header(None)) -> list:
    if token is None:
        return []
    try:
        dict_token = jwt.decode(token, get_settings().secret_key, algorithms=get_settings().jwt_algorithms)
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid token format")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token expired")
    return dict_token["scopes"]


def raise_not_authorized(user_scopes: list, required_scopes: list) -> bool:
    if not set(required_scopes).issubset(set(user_scopes)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Do not have permissions for this action")
    return True
