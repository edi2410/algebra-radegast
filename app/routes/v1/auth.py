from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.db import SessionDep
from app.core.metrics import track_endpoint_metrics, auth_login_attempts, auth_registrations
from app.models.auth import Token, LoginData
from app.models.user import UserCreate
from app.services.auth_services import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)



@router.post("/token", response_model=Token)
@track_endpoint_metrics("auth_login")
async def login_for_access_token(
        form_data: Annotated[LoginData, Depends()],
        session: SessionDep,
) -> Token:
    try:
        access_token = AuthService.login_user(session, form_data.email, form_data.password)
        auth_login_attempts.labels(status='success').inc()
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        auth_login_attempts.labels(status='failed').inc()
        raise


@router.post("/token/register", response_model=Token)
@track_endpoint_metrics("auth_register")
async def register_user(
        user: UserCreate,
        session: SessionDep,
) -> Token:
    try:
        access_token = AuthService.register_and_login_user(session, user)
        auth_registrations.labels(status='success').inc()
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        auth_registrations.labels(status='failed').inc()
        raise