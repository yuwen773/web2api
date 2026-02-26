from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    account: str
    password: str
    code: str = ""
    captcha: str = ""
    invite: str = ""
    agreement: bool = True


class TokenData(BaseModel):
    token: str
    email: str
    phone: str
    role: str


class LoginResponse(BaseModel):
    code: int
    data: Optional[TokenData] = None
    msg: str = ""
