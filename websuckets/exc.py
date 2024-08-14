from typing import Optional

from .models import ErrorModel
from .types import IO_TYPE


class InternalError(Exception):
    def __init__(self, error: str, payload: Optional[IO_TYPE] = None):
        self.error = ErrorModel(
            error=error,
            details=payload
        )


class DuplicateEventName(InternalError):
    def __init__(self, event_name):
        super().__init__("недопустимый дубликат", f"событие с именем {event_name} уже существует")


class InvalidHandlerSignature(InternalError):
    def __init__(self, details: str):
        super().__init__("неверная сигнатура обработчика",
                         details)

class EmptyPayload(InternalError):
    def __init__(self):
        super().__init__("отсутствует поле payload", f"для этого события поле payload обязательно")


class OutputError(InternalError):
    def __init__(self):
        super().__init__("Неверный возвращаемый тип обработчика")


class NotAuthorized(InternalError):
    def __init__(self):
        super().__init__("вы не авторизованы")


class EventNotFound(InternalError):
    def __init__(self, event_name: str):
        super().__init__("неизвестная команда", f"команды {event_name} не существует")


class InvalidJSON(InternalError):
    def __init__(self, details):
        super().__init__("невалидный JSON", details)


class UnexpectedArgumentError(InternalError):
    def __init__(self, details: str):
        super().__init__("неизвестное поле", details)


class UserNotFound(InternalError):
    def __init__(self):
        super().__init__("пользователь не найден")


class InvalidPassword(InternalError):
    def __init__(self):
        super().__init__("неверный пароль")
