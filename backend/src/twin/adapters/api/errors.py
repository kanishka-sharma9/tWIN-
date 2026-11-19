"""One error shape for every non-2xx response.

{"error": {"code": "pair_taken", "message": "...", "details": {}}}
"""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from twin.domain.errors import DomainError

logger = logging.getLogger(__name__)


class ErrorBody(BaseModel):
    code: str = Field(description="Stable snake_case code the UI switches on.")
    message: str = Field(description="English text for display.")
    details: dict[str, object] = Field(
        default_factory=dict, description='Extra context, e.g. {"field": "alter"}.'
    )


class ErrorResponse(BaseModel):
    error: ErrorBody


# The one table mapping domain error classes to an HTTP status. Each feature story adds its
# own rows; an error class that is not listed answers 400.
STATUS_BY_ERROR: dict[type[DomainError], int] = {}

_CODE_BY_STATUS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
}

# Attached to the API router so every route documents the shape in OpenAPI.
ERROR_RESPONSES: dict[int | str, dict[str, object]] = {
    status: {"model": ErrorResponse, "description": HTTPStatus(status).phrase}
    for status in (400, 401, 403, 404, 405, 409, 422, 500)
}


def error_response(
    status: int, code: str, message: str, details: dict[str, object] | None = None
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or {})
    )
    return JSONResponse(status_code=status, content=body.model_dump())


def _status_for(error: DomainError) -> int:
    # List the more specific classes first.
    for cls, status in STATUS_BY_ERROR.items():
        if isinstance(error, cls):
            return status
    return 400


async def _domain_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    return error_response(_status_for(exc), exc.code, exc.message, exc.details)


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    fields = [
        {"field": ".".join(str(part) for part in err["loc"][1:]), "reason": err["msg"]}
        for err in jsonable_encoder(exc.errors())
    ]
    return error_response(
        422, "validation_error", "The request is not valid.", {"fields": fields}
    )


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = _CODE_BY_STATUS.get(exc.status_code, f"http_{exc.status_code}")
    message = str(exc.detail) if exc.detail else HTTPStatus(exc.status_code).phrase
    return error_response(exc.status_code, code, message)


async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception", exc_info=exc)
    return error_response(500, "internal_error", "Something went wrong on our side.")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unhandled)
