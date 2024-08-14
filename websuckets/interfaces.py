from abc import ABC, abstractmethod
from typing import Type, Callable

from pydantic import BaseModel
from websockets import WebSocketServerProtocol


class BaseEvent(ABC):
    def __init__(self,
                 name: str,
                 model: Type[BaseModel] | None):
        self.name = name
        self.model = model

    @abstractmethod
    async def __call__(self, socket: WebSocketServerProtocol, data: dict): ...


class Event:
    def __init__(self,
                 name: str,
                 model: Type[BaseModel] | None = None,
                 protected: bool = False):
        self.name = name
        self.model = model
        self.protected = protected
        self.handler: Callable = ...



