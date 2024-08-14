from typing import Callable

from pydantic import BaseModel

from .types import IO_TYPE, PAYLOAD


class InputModel(BaseModel):
    event: str
    payload: dict | None = None
    token: str | None = None


class OutputModel(BaseModel):
    event: str
    payload: IO_TYPE | None = None


class HandlerModel(BaseModel):
    func: Callable
    protected: bool


class ErrorModel(BaseModel):
    error: str
    details: IO_TYPE | None


class EventModel(BaseModel):
    event: Callable
    payload: PAYLOAD | None = None
    token: str | None = None
