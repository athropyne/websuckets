from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

from .interfaces import BaseEvent


SOCKET_ID = UUID
IO_TYPE = str | int | dict | list
USER_ID = str | int
EVENT_CLASS = TypeVar("EVENT_CLASS", bound=BaseEvent)
PAYLOAD = TypeVar("PAYLOAD", bound=BaseModel)

