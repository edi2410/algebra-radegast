from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select

from app.config.config import settings
from app.models.user import UserCreate, User
from app.services.user_services import UserService

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()

        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                role=User.Role.ADMIN,
            )
            UserService.create_user(session=session, user=user_in)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
