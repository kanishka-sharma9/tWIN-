from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Request, Response
from pydantic import BaseModel, Field, SecretStr, field_validator

from twin.adapters.api.csrf import require_csrf
from twin.adapters.api.dependencies import get_current_user
from twin.application.change_password import ChangePassword
from twin.application.sessions import Sessions, SessionTokens
from twin.application.sign_up import SignUp
from twin.domain.email import Email, InvalidEmail
from twin.domain.vault import User
from twin.settings import Settings

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"
# The cookie is only sent to the auth routes, never to vault or file routes.
REFRESH_COOKIE_PATH = "/api/auth"


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


class LoginRequest(BaseModel):
    # Not validated as strictly as signup: a malformed email is just a wrong login.
    email: str = Field(max_length=320)
    password: SecretStr = Field(max_length=1024)


class ChangePasswordRequest(BaseModel):
    # The current password is not length-checked: a wrong one is a 401, not a format error.
    current_password: SecretStr = Field(max_length=1024)
    # Length rules (10 to 128) are applied by the use case and answer 422 weak_password;
    # the cap here only bounds the work an oversized body can cause.
    new_password: SecretStr = Field(max_length=1024)


class UserOut(BaseModel):
    id: UUID
    email: str
    has_password: bool = Field(
        description="False for an account made with Google only."
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until the access token expires.")
    user: UserOut


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id, email=user.email.value, has_password=user.password_hash is not None
    )


def get_sign_up(request: Request) -> SignUp:
    sign_up: SignUp = request.app.state.sign_up
    return sign_up


def get_change_password(request: Request) -> ChangePassword:
    change_password: ChangePassword = request.app.state.change_password
    return change_password


def get_sessions(request: Request) -> Sessions:
    sessions: Sessions = request.app.state.sessions
    return sessions


def set_refresh_cookie(
    request: Request, response: Response, tokens: SessionTokens
) -> None:
    settings: Settings = request.app.state.settings
    response.set_cookie(
        REFRESH_COOKIE,
        tokens.refresh_token,
        max_age=tokens.refresh_expires_in,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    response.headers["Cache-Control"] = "no-store"


def _respond(
    request: Request, response: Response, tokens: SessionTokens
) -> TokenResponse:
    set_refresh_cookie(request, response, tokens)
    return TokenResponse(
        access_token=tokens.access_token,
        expires_in=tokens.expires_in,
        user=_user_out(tokens.user),
    )


@router.post("/signup", status_code=201)
def sign_up(
    body: SignUpRequest,
    request: Request,
    response: Response,
    use_case: Annotated[SignUp, Depends(get_sign_up)],
    sessions: Annotated[Sessions, Depends(get_sessions)],
) -> TokenResponse:
    user = use_case.execute(body.email, body.password.get_secret_value())
    return _respond(request, response, sessions.start(user))


@router.post("/login")
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    sessions: Annotated[Sessions, Depends(get_sessions)],
) -> TokenResponse:
    client = request.client.host if request.client else "unknown"
    tokens = sessions.login(body.email, body.password.get_secret_value(), client)
    return _respond(request, response, tokens)


@router.post("/refresh", dependencies=[Depends(require_csrf)])
def refresh(
    request: Request,
    response: Response,
    sessions: Annotated[Sessions, Depends(get_sessions)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    return _respond(request, response, sessions.refresh(refresh_token))


@router.post("/logout", status_code=204, dependencies=[Depends(require_csrf)])
def logout(
    response: Response,
    sessions: Annotated[Sessions, Depends(get_sessions)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    sessions.logout(refresh_token)
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)


@router.get("/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return _user_out(user)


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ChangePassword, Depends(get_change_password)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    """Change the password; the login session of this request stays, all others end."""
    use_case.execute(
        user.id,
        body.current_password.get_secret_value(),
        body.new_password.get_secret_value(),
        use_case.family_of(user.id, refresh_token),
    )
