from datetime import timedelta, datetime, timezone

import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends

from app.config.config import settings
from app.core.db import SessionDep
from app.models.user import User, Role
from app.services.security_services import SecurityService
from app.services.user_services import UserService

security = HTTPBearer()


class AuthService:

    @staticmethod
    def get_user(session: Session, email: str) -> User | None:
        statement = select(User).where()
        result = session.exec(statement).first()
        return result

    @staticmethod
    def authenticate_user(session, email: str, password: str):
        user = AuthService.get_user(session, email)
        if not user:
            return False
        if not SecurityService.verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def login_user(session: Session, email: str, password: str) -> str:
        user = AuthService.authenticate_user(session, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return _generate_token(user)

    @staticmethod
    def register_and_login_user(session: Session, user_create) -> str:
        new_user = UserService.create_user(session, user_create)
        return _generate_token(new_user)

    @staticmethod
    def get_current_user(
            session: SessionDep,
            credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> User:
        token = credentials.credentials
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
        user = AuthService.get_user(session, email)
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def require_creator_or_admin(
            current_user: User = Depends(get_current_user)
    ) -> User:
        print(f"Current user role: {current_user.role}")

        if current_user.role == Role.GUEST:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only content creator and admin can perform this action.",
            )
        return current_user


def _generate_token(user: User) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return AuthService.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
