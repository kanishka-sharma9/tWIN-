from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from twin.adapters.api.dependencies import get_session
from twin.adapters.persistence.accounts import (
    SqlFolderRepository,
    SqlUnitOfWork,
    SqlUserRepository,
    SqlVaultRepository,
)
from twin.application.create_user import CreateUser
from twin.application.ports.security import PasswordHasher
from twin.domain.accounts import PASSWORD_MAX_LENGTH
from twin.domain.accounts import User as DomainUser

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: str = Field(description="Email address; compared ignoring letter case.")
    # Length is judged by the domain rules (a clear weak_password code), not here; this cap
    # only keeps an absurd body from reaching the hasher.
    password: str = Field(max_length=PASSWORD_MAX_LENGTH * 4, repr=False)


class UserOut(BaseModel):
    id: UUID
    email: str


class SignupResponse(BaseModel):
    user: UserOut


def _user_out(user: DomainUser) -> UserOut:
    return UserOut(id=user.id, email=user.email)


@router.post("/signup", status_code=201)
def signup(
    body: SignupRequest,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> SignupResponse:
    hasher: PasswordHasher = request.app.state.password_hasher
    clock = request.app.state.clock
    create = CreateUser(
        SqlUserRepository(session),
        SqlVaultRepository(session),
        SqlFolderRepository(session),
        SqlUnitOfWork(session),
        clock,
        hasher,
    )
    account = create(body.email, body.password)
    return SignupResponse(user=_user_out(account.user))
