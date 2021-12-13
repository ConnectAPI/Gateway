from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
import jwt

from ..core.schemas.token import NewTokenForm, Token
from ..core.models.db import get_db
from ..core.settings import get_settings
from ..validation import check_client_scopes


token_endpoint = APIRouter(prefix="/token", tags=["token"])


def create_jwt_token(scopes: list, tid: str):
    encoded_token = jwt.encode(
        key=get_settings().secret_key,
        payload={
            "scopes": scopes,
            "tid": tid,
            "exp": (datetime.now() + timedelta(seconds=get_settings().jwt_lifetime)).timestamp()
        },
        algorithm=get_settings().jwt_algorithms[0]
    )
    return encoded_token


@token_endpoint.put("", status_code=201)
def create_token(
        new_key: NewTokenForm,
        user_scopes: list = Depends(check_client_scopes)
):
    db = get_db()
    if "token:create" not in user_scopes and get_settings().super_user_scope not in user_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have the permission to create token (token:create) {user_scopes}"
        )
    if "token:create" in new_key.scopes and get_settings().super_user_scope not in user_scopes:
        # Only allow super user to create tokens that create tokens
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permissions for this action (required super user key)"
        )
    if not set(new_key.scopes).issubset(set(get_settings().allowed_scopes)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="some scopes are not exist"
        )
    token = Token(scopes=new_key.scopes)
    encoded_token = create_jwt_token(token.scopes, token.tid)
    db.tokens.insert_one(token.dict())
    return {"token": encoded_token, "id": token.tid, "refresh_token": token.refresh_token}


@token_endpoint.delete("")
def delete(
        token_id: str,
        user_scopes: list = Depends(check_client_scopes)
):
    db = get_db()
    if "token:delete" not in user_scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permissions to delete token")
    result = db.tokens.delete_one({"tid": token_id})
    return {"deleted": result.deleted_count > 0}


@token_endpoint.get("")
def get_token(token_id: str, user_scopes: list = Depends(check_client_scopes)):
    db = get_db()
    if "token:read" not in user_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to get the token"
        )
    base_filter = {"_id": 0, "refresh_token": 0}
    token_data = db.tokens.find_one({"tid": token_id}, base_filter)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return {"token": token_data}


@token_endpoint.post("/refresh")
def refresh(refresh_token: str):
    db = get_db()
    token = db.tokens.find_one({"refresh_token": refresh_token, "active": True})
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")

    encoded_token = create_jwt_token(token["scopes"], token["tid"])
    return encoded_token


@token_endpoint.get("/list")
def tokens_list(user_scopes: list = Depends(check_client_scopes)):
    db = get_db()
    if "super_user" not in user_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to get tokens list"
        )
    tokens = list(db.tokens.find({}, {"_id": 0}))
    return {"tokens": tokens}


@token_endpoint.post("/deactivate")
def deactivate(
        token_id: str,
        user_scopes: list = Depends(check_client_scopes)
):
    db = get_db()
    if "token:delete" not in user_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to deactivate token 'token:delete' scope"
        )
    result = db.tokens.update_one({"tid": token_id}, {"active": False})
    return {"deactivate": result.deleted_count > 0}
