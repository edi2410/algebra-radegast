from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.user import UserCreate, User
from app.services.security_services import SecurityService


class UserService:

    @staticmethod
    def get_user_by_email(session: Session, email: str) -> User | None:
        return session.exec(
            select(User).where(User.email == email)
        ).first()

    @staticmethod
    def create_user(session: Session, user: UserCreate) -> User:
        existing_user = UserService.get_user_by_email(session, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = SecurityService.get_hashed_value(user.password)
        new_user = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
