from pydantic import EmailStr
from sqlmodel import SQLModel

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: EmailStr | None = None

class LoginData(SQLModel):
    email: str
    password: str
