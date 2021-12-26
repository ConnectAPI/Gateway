from fastapi import Header, HTTPException, status, Depends
import jwt

from .core.settings import get_settings


def check_super_user_permissions(super_user_secret: str = Header(None)) -> bool:
    if super_user_secret is None:
        return False
    if super_user_secret != get_settings().super_user_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid super user secret"
        )
    return True


def check_client_scopes(token: str = Header(None), is_super_user: bool = Depends(check_super_user_permissions)):
    if is_super_user:
        return get_settings().allowed_scopes + [get_settings().super_user_scope]
    if token is None:
        return []
    try:
        dict_token = jwt.decode(token, get_settings().secret_key, algorithms=get_settings().jwt_algorithms)
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
            headers={"x-auth-exception": "Invalid"}
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid token format",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token expired",
            headers={"x-auth-exception": "Expired"}
        )
    return dict_token["scopes"]
