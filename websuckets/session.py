from typing import Dict

from websockets import WebSocketServerProtocol

from .exc import InternalError
from .types import SOCKET_ID, USER_ID


class User:
    def __init__(self,
                 socket: WebSocketServerProtocol):
        self.socket = socket
        self._id: USER_ID | None = None
        self._token: str | None = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is None:
            if self._id in Session.verified:
                del Session.verified[self._id]
        else:
            self._id = value
            Session.verify(self)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        Session.verify(self)
        self._token = value


class Session:
    online: Dict[SOCKET_ID, User] = {}
    verified: Dict[USER_ID, User] = {}

    @classmethod
    def add(cls, socket: WebSocketServerProtocol):
        cls.online[socket.id] = User(socket)

    @classmethod
    def verify(cls, user: User):
        cls.verified[user.id] = user

    @classmethod
    def remove(cls, socket):
        user: User = cls.online[socket.id]
        if user.id is not None:
            del cls.verified[user.id]
        del cls.online[socket.id]


