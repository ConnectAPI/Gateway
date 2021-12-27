from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status, Request, Header
import jwt

from core.schemas.token import NewTokenForm, Token
from core.models.db import get_db
from core.settings import get_settings
from core.models.auth import auth_flow


__all__ = ["auth_router"]

auth_router = APIRouter(prefix="/token", tags=["token"])


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


@auth_router.put("", status_code=201)
async def create_token(
        r: Request,
        new_key: NewTokenForm,
        super_user_secret: str = Header(default=None)
):
    """Create new token with permission scopes"""
    db = get_db()
    if get_settings().super_user_scope in new_key.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can't add superuser scope to token pass it as separate header"
        )

    endpoint_required_scopes = ["token:create"]
    if "token:create" in new_key.scopes:
        endpoint_required_scopes.append(get_settings().super_user_scope)

    print(super_user_secret)
    if super_user_secret != get_settings().super_user_secret:
        await auth_flow(r, required_scopes=endpoint_required_scopes)

    token = Token(scopes=new_key.scopes)
    encoded_token = create_jwt_token(token.scopes, token.tid)
    db.tokens.insert_one(token.dict())
    return {"token": encoded_token, "id": token.tid, "refresh_token": token.refresh_token}


@auth_router.delete("")
async def delete(r: Request, token_id: str):
    db = get_db()
    await auth_flow(r, required_scopes=["token:delete"])

    result = db.tokens.delete_one({"tid": token_id})
    return {"deleted": result.deleted_count > 0}


@auth_router.get("")
async def get_token(r: Request, token_id: str):
    db = get_db()
    await auth_flow(r, required_scopes=["token:read"])

    base_filter = {"_id": 0, "refresh_token": 0}
    token_data = db.tokens.find_one({"tid": token_id}, base_filter)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return {"token": token_data}


@auth_router.post("/refresh")
async def refresh(refresh_token: str):
    db = get_db()
    token = db.tokens.find_one({"refresh_token": refresh_token, "active": True})
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")

    encoded_token = create_jwt_token(token["scopes"], token["tid"])
    return encoded_token


@auth_router.get("/list")
async def tokens_list(r: Request):
    db = get_db()
    await auth_flow(r, required_scopes=[get_settings().super_user_scope])

    tokens = list(db.tokens.find({}, {"_id": 0}))
    return {"tokens": tokens}


@auth_router.post("/deactivate")
async def deactivate(r: Request, token_id: str):
    db = get_db()
    await auth_flow(r, required_scopes=["token:delete"])

    result = db.tokens.update_one({"tid": token_id}, {"active": False})
    return {"deactivate": result.deleted_count > 0}
