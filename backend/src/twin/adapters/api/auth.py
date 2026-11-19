from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field, SecretStr, field_validator

from twin.application.sign_up import SignUp
from twin.domain.email import Email, InvalidEmail

router = APIRouter(prefix="/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: str = Field(description="Email address; compared ignoring case.")
    # SecretStr keeps the password out of reprs, validation-error inputs and OpenAPI examples.
    password: SecretStr = Field(description="10 to 128 characters, no other rules.")

    @field_validator("email")
    @classmethod
    def _email_is_valid(cls, value: str) -> str:
        try:
            return Email(value).value
        except InvalidEmail as error:
            raise ValueError(error.message) from error


class UserOut(BaseModel):
    id: UUID
    email: str


class SignUpResponse(BaseModel):
    user: UserOut


def get_sign_up(request: Request) -> SignUp:
    sign_up: SignUp = request.app.state.sign_up
    return sign_up


@router.post("/signup", status_code=201)
def sign_up(
    body: SignUpRequest, use_case: Annotated[SignUp, Depends(get_sign_up)]
) -> SignUpResponse:
    user = use_case.execute(body.email, body.password.get_secret_value())
    return SignUpResponse(user=UserOut(id=user.id, email=user.email.value))
