import asyncio
import uuid

from pydantic import BaseModel
from websockets import WebSocketServerProtocol

from websuckets import WebSuckets, CommandGroup, ClientEvent
from websuckets.exc import InternalError
from websuckets.security import Token
from websuckets.session import Session

app = WebSuckets()
group = CommandGroup()


class CreateModel(BaseModel):
    login: str
    password: str


DATABASE = []  # база данных


class UserNotFound(InternalError):
    def __init__(self):
        super().__init__("пользователь не найден")


class InvalidPassword(InternalError):
    def __init__(self):
        super().__init__("неверный пароль")


@group.command("create")
async def create(socket: WebSocketServerProtocol, model: CreateModel):
    for i in DATABASE:
        if i["login"] == model.login:
            raise InternalError("дубль", "Пользователь с таким логином уже существует")

    user_id = uuid.uuid4()  # создаем id пользователя
    user_data = model.model_dump()  # создаем словарь из модели
    user_data["id"] = str(user_id)
    DATABASE.append(user_data)
    await socket.send(ClientEvent("user created"))


@group.command("auth")
async def auth(socket: WebSocketServerProtocol, model: CreateModel):
    for i in DATABASE: # проходим по всей базе
        if i["login"] == model.login: # если такой логин есть
            if i["password"] != model.password: # но пароли не совпадают
                raise InvalidPassword # выбрасываем ошибку
            token = Token.generate() # если паролт совпадают, генерируем токен
            current_user = Session.online[socket.id] # плучаем текущего пользователя
            current_user.id = i["id"] # обязательно запоминаем id
            current_user.token = token # обязательно запоминаем токен
            current_user.login = i["login"] # можно запомнить все что угодно, например логин
            event = ClientEvent("new token", token) # создаем событие для клиета
            await socket.send(event) # отправляем событие клиенту
            return # выходим из функции
    raise UserNotFound # если логин не найден выкидываем ошибку


@group.command("get list", protected=True)
async def get_list(socket: WebSocketServerProtocol):
    users = [{k: v for k, v in i.items() if k != "password"} for i in DATABASE] # фильтруем данные от паролей
    client_event = ClientEvent("users list", users)
    await socket.send(client_event)


app.include_command_group(group)

app = WebSuckets()
if __name__ == '__main__':
    asyncio.run(app("localhost", 9000))
