import asyncio
import functools
import inspect
from traceback import print_tb
from typing import List, Callable, Type, Any, Awaitable, Coroutine

import websockets
from pydantic import ValidationError, BaseModel
from websockets import WebSocketServerProtocol

from . import exc
from .exc import InternalError, EventNotFound, DuplicateEventName, InvalidHandlerSignature, EmptyPayload, InvalidJSON, \
    NotAwaitableHandler
from .models import InputModel, HandlerModel
from .security import Token
from .session import Session, User


class EventList:
    events = {}


class CommandGroup:
    def __init__(self, prefix: str = ""):
        self.prefix = prefix + " " if len(prefix) > 0 else prefix
        self._commands = {}

    @property
    def commands(self):
        return self._commands

    def command(self, name: str, protected: bool = False):
        def decorator(func: Callable):
            if not inspect.iscoroutinefunction(func):
                raise InvalidHandlerSignature(func.__name__)
            sig = inspect.signature(func)
            parameters = list(sig.parameters.values())
            match len(parameters):
                case 0:
                    raise InvalidHandlerSignature(
                        "обработчик должен принимать первым параметром объект WebSocketServerProtocol и быть аннотирован")
                case 1:
                    if parameters[0].annotation is not WebSocketServerProtocol:
                        raise InvalidHandlerSignature(
                            "обработчик должен принимать первым параметром объект WebSocketServerProtocol и быть аннотирован")
                case 2:
                    if parameters[0].annotation is not WebSocketServerProtocol:
                        raise InvalidHandlerSignature(
                            "обработчик должен принимать первым параметром объект WebSocketServerProtocol и быть аннотирован")
                    if parameters[1].annotation is inspect.Parameter.empty:
                        raise InvalidHandlerSignature("параметр обработчика должен быть аннотирован")
                    if not issubclass(parameters[1].annotation, BaseModel):
                        raise InvalidHandlerSignature("обработчик может принимать только модель Pydantic")
                    if parameters[1].annotation is inspect.Parameter.empty:
                        raise InvalidHandlerSignature("параметр обработчика должен быть аннотирован")
                    if not issubclass(parameters[1].annotation, BaseModel):
                        raise InvalidHandlerSignature("обработчик может принимать только модель Pydantic")
            if len(sig.parameters) > 2:
                raise InvalidHandlerSignature("обработчик может принимать не более двух параметров")
            for k, v in self._commands.items():
                if self.prefix + name == k:
                    raise DuplicateEventName(k)
            self._commands[self.prefix + name] = HandlerModel(func=func, protected=protected)

            @functools.wraps(func)
            async def wrapper():
                ...

            return wrapper

        return decorator


class _MessageParser:
    def __init__(self, message: str | bytes):
        self.message = message
        self.serialized: InputModel = ...
        try:
            self.serialized = InputModel.model_validate_json(self.message)
        except ValidationError as e:
            _MessageParser.__error_parser(e)


    @classmethod
    def __error_parser(cls, e: ValidationError):
        errors = e.errors(include_url=False, include_input=False)
        err_output: List[str] = []
        for i in errors:
            if i["type"] == "json_invalid":
                raise InvalidJSON(str(e))
            elif i["type"] == "missing":
                err_output.append(f"пропущено поле '{i['loc'][0]}'")
            elif i["type"].endswith("_type"):
                err_output.append(f"неверный тип поля '{i['loc'][0]}'")
            elif i["type"] == "enum":
                err_output.append(f"поле '{i['loc'][0]}' может принимать только значения: {i['ctx']}")
            else:
                err_output.append(str(i))

        if err_output:
            raise exc.ValidationError(err_output)

    @classmethod
    def validate(cls, model_class: Type[BaseModel], values: dict):
        if values is None:
            raise EmptyPayload
        try:
            return model_class(**values)
        except ValidationError as e:
            cls.__error_parser(e)

    def separate(self) -> tuple[str, dict | None, str | None]:
        return self.serialized.event, self.serialized.payload, self.serialized.token


class _HandlerParser:
    def __init__(self, event: str):
        self.event = event
        handler_model: HandlerModel = EventList.events.get(self.event)
        if handler_model is None:
            raise EventNotFound(self.event)
        self._func = handler_model.func
        self._protected = handler_model.protected

    def separate(self) -> tuple[Callable[..., Any], bool]:
        return self._func, self._protected

    def check_protected(self, user: User, token: str):
        if self._protected:
            Token.verify(user, token)
        return self


class WebSuckets:

    async def _adapter(self, func: Callable):
        @functools.wraps(func)
        async def wrapper(socket: WebSocketServerProtocol, model: dict | None):
            sig = inspect.signature(func)
            parameters = list(sig.parameters.values())
            if len(parameters) == 2:
                model_class = list(sig.parameters.values())[1].annotation
                model = _MessageParser.validate(model_class, model)
            try:
                await func(socket, model) if model is not None else await func(socket)
            except TypeError as e:
                raise e

        return wrapper

    async def _handler(self, socket: WebSocketServerProtocol):
        Session.add(socket)
        print(f"клиент {socket.id} подключен")
        while True:
            for k, v in Session.verified.items():
                print(k, v)
            try:
                message = await socket.recv()
                event, payload, token = _MessageParser(message).separate()
                handler, protected = _HandlerParser(event).check_protected(Session.online[socket.id], token).separate()
                delegate = await self._adapter(handler)

                await delegate(socket, payload)

            except InternalError as e:
                await socket.send(e.error.model_dump_json())
            except ValidationError as e:
                await socket.send(str(e))
            except websockets.exceptions.ConnectionClosed:
                Session.remove(socket)
                print(f"клиент {socket.id} отключен")
                break
            except Exception as e:
                print_tb(e.__traceback__)
                print(e.__class__)
                print(str(e))
                await socket.send(str(e))

    def include_command_group(self, group: CommandGroup):
        for event_name, handler in group.commands.items():
            if event_name in EventList.events:
                raise DuplicateEventName(event_name)
            EventList.events[event_name] = handler

    async def __call__(self, host: str, port: int):
        async with websockets.serve(self._handler, host=host, port=port):
            print(f"сервер запущен ws://{host}:{port}")
            await asyncio.Future()
