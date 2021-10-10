from secrets import token_urlsafe
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from context import get_db, get_settings
from ..security import auth_flow

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/token")
def get_token(login_form: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    tuid = str(uuid4())
    token = auth_flow.generate_jwt(login_form.username, scopes=login_form.scopes, tuid=tuid)
    refresh_token = token_urlsafe(40)
    db.sessions.insert_one(
        {
            "tuid": tuid,
            "scopes": login_form.scopes,
            "username": login_form.username,
            "password": login_form.password,
            "refresh_token": refresh_token,
            "active": True,
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires": get_settings().auth_jwt_lifespan.seconds
    }


@auth_router.post("/refresh_token")
def refresh(refresh_token: str, token: dict = Depends(auth_flow)):
    db = get_db()
    tuid = token["tuid"]
    if not db.sessions.find_one({"tuid": tuid, "refresh_token": refresh_token, "active": True}, {"_id"}):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive session")
    refreshed_token = auth_flow.generate_jwt(user_id=token["sub"], scopes=token["scopes"], tuid=tuid)
    return {
        "access_token": refreshed_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires": get_settings().auth_jwt_lifespan.seconds
    }
