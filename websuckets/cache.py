from typing import Dict

from websockets import WebSocketServerProtocol

from .types import SOCKET_ID


class Cache:
    online: Dict[SOCKET_ID, WebSocketServerProtocol] = {}

    @classmethod
    def add(cls, socket: WebSocketServerProtocol):
        cls.online[socket.id] = socket

    @classmethod
    def remove(cls, socket):
        del cls.online[socket.id]
