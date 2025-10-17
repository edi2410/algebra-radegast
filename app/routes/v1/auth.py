from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.db import SessionDep
from app.models.auth import Token, LoginData
from app.models.user import UserCreate
from app.services.auth_services import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.post("/token",  response_model=Token)
async def login_for_access_token(
        form_data: Annotated[LoginData, Depends()],
        session: SessionDep,
) -> Token:
    access_token = AuthService.login_user(session, form_data.email, form_data.password)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token/register", response_model=Token)
async def register_user(
        user: UserCreate,
        session: SessionDep,
) -> Token:
    access_token = AuthService.register_and_login_user(session, user)
    return Token(access_token=access_token, token_type="bearer")
