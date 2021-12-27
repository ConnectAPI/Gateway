from typing import List
from secrets import token_urlsafe
from datetime import datetime

from pydantic import BaseModel, Field


class NewTokenForm(BaseModel):
    scopes: List[str] = Field(default_factory=list)


class Token(BaseModel):
    tid: str = Field(default_factory=lambda: token_urlsafe(15))
    refresh_token: str = Field(default_factory=lambda: token_urlsafe(20))
    scopes: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = True
