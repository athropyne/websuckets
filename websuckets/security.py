import random
import uuid
from _md5 import md5
from typing import Callable

from websockets import WebSocketServerProtocol

from .exc import NotAuthorized
from .session import Session, User
from .types import PAYLOAD


class Token:
    @staticmethod
    def generate() -> str:
        return uuid.uuid4().hex

    @staticmethod
    def verify(user: User, token: str):
        if token is None or user.token != token:
            raise NotAuthorized


def protected(func: Callable):
    async def wrapper(socket: WebSocketServerProtocol, model: PAYLOAD | None = None, token: str | None = None):
        if Session.online[socket.id].token == token:
            await func(socket, model)
        else:
            await socket.send("вы не авторизованы")
    return wrapper