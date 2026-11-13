from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from twin.adapters.api.dependencies import get_session

router = APIRouter()


class Health(BaseModel):
    status: Literal["ok"]
    database: Literal["up", "down"]


@router.get("/health")
def health(session: Annotated[Session, Depends(get_session)]) -> Health:
    # Reports readiness without becoming a failing liveness probe: always 200.
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return Health(status="ok", database="down")
    return Health(status="ok", database="up")
