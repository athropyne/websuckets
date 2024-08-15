from pydantic import BaseModelfrom websuckets import WebSucketsfrom websuckets import WebSucketsfrom websuckets import WebSuckets

# Websuckets
## О проекте

Надстройка над `websockets` 
для упрощенной работы с приложениями реального времени, 
использующая библиотеку `pydantic` для валидации данных.

### Установка

`pip install websuckets`

### Объект WebSuckets

Для создания приложения создайте объект `WebSuckets`.

```python
from websuckets import WebSuckets
app = WebSuckets()
```

В данном примере `app` - вызываемый асинхронный объект с двумя параметрами **host: str** и **port: int**.

Запустите ее с помощью метода `asyncio.run`:

`asyncio.run(app('localhost', 9000))`

В консоли должно появиться сообщение об успешном запуске сервера

###### Полный код:

```python
import asyncio
from websuckets import WebSuckets

app = WebSuckets()

if __name__ == '__main__':
    asyncio.run(app("localhost",9000))
```

### Клиент
Для подключения к серверу вы можете 
использовать консольный клиент предоставляемый
библиотекой `websockets`. 
Откройте терминал (или другую вкладку) и выполните команду 

`python -m websockets ws://localhost:9000`

Вы увидете приглашение для ввода сообщений

### События (команды)

Команды представляют собой JSON объекты с как минимум одним обязательным ключом `event` со строковым содержимым:

`{"event":"get all users"}`

Так же объект может содержать необязательные ключи: 
`payload` - полезная нагрузка. Представляет собой вложенный объект json с любыми полями

и 

`token` - токен подлинности. Представляет строку которая дает доступ к приватным командам

###### Примеры:

`{"event":"get all posts"}`

`{"event":"create", "payload": {"login":"athropyne", "password":"SecretpaSSword"}}`

`{"event":"get all users", "token":"23a3bb3c3234ba27be33b2b5523acf3"}`



На данный момент нет ни одной зарегистрированной команды
поэтому на любое сообщение от клиента вы получите ошибку.

Чтобы создать команду создайте группу команд `CommandGroup`,
зарегистрируйте с помощью нее обработчик и добавьте группу к списку команд с помощью метода `include_command_group`:

```python
import asyncio

from websockets import WebSocketServerProtocol

from websuckets import WebSuckets, CommandGroup

app = WebSuckets()
group = CommandGroup()


@group.command("say ok", protected=False)
async def create(socket: WebSocketServerProtocol):
    await socket.send("ok")


app.include_command_group(group)

app = WebSuckets()
if __name__ == '__main__':
    asyncio.run(app("localhost", 9000))
```
В этом случае обработчик будет реагировать на ввод 
`{"event":"say ok"}`

Декоратор `@group.command` принимает 2 параметра:

`name` - тип `str` - имя команды

`protected` - тип `bool` - приватная команда или нет,
по умолчанию False


Объект `CommandGroup` может принимать аргумент `prefix`,
если его указать - все команды группы будут начинаться с этого префикса + пробел.

```python
import asyncio

from websockets import WebSocketServerProtocol

from websuckets import WebSuckets, CommandGroup

app = WebSuckets()
group = CommandGroup("test")


@group.command("say ok", protected=False)
async def create(socket: WebSocketServerProtocol):
    await socket.send("ok")


app.include_command_group(group)

app = WebSuckets()
if __name__ == '__main__':
    asyncio.run(app("localhost", 9000))
```
Теперь обработчик будет реагировать на 

`{"event":"test say ok"}`

Все команды в программе должны быть с уникальным именем.

### Обработчики

Обработчик - асинхронная функция, 
объявленная под декоратором `CommandGroup.command`.

Каждый обработчик должен принимать строго либо 1 либо 2 параметра:

Первый параметр обязательный и должен быть аннотирован типом 
`WebSocketServerProtocol`

###### Напирмер:

```python
async def create(socket: WebSocketServerProtocol): ...
```

Второй параметр не обязательный и представляет модель данных
`pydantic.BaseModel` и так же должен быть аннотирован.

0 или больше 2 параметров в обработчике, не аннотированные параметры - вызовут ошибку.

##### Например:

```python
import asyncio

from pydantic import BaseModel

from websockets import WebSocketServerProtocol

from websuckets import WebSuckets, CommandGroup

app = WebSuckets()
group = CommandGroup("user")

class CreateModel(BaseModel):
    nickname: str
    password: str
    


@group.command("create", protected=False)
async def create(socket: WebSocketServerProtocol, model: CreateModel):
    await socket.send(model.model_dump_json())


app.include_command_group(group)

app = WebSuckets()
if __name__ == '__main__':
    asyncio.run(app("localhost", 9000))
```

класс CreateModel представляет класс данных и будет 
ожидать описанные в нем поля в поле `payload`.

Откройте терминал и запустите клиент :

`python -m websockets ws://localhost:9000`

и попробуйте ввести такую строку:

`{"event":"user create", "payload": {"nickname":"athropyne","password":"SecretpaSSword"}}`

Это должно вернуть данные из поля `payload`

Вызов **await socket.send("message")**, как наверное уже понятно
нужен для отправки сообщения на клиент. Их можно отправить сколько 
угодно из одного обработчика или не отправлять вообще.
Подробности смотри в документации к `websockets` 
(https://websockets.readthedocs.io)


### Сессии

Каждый подключенный клиент сохраняется в сессии,
а конкретно в классе `Session` где есть 2 статических поля:

`online: Dict[UUID, User]` - хранящий всех подключенных клиентов 

и 

`verified: Dict[str | int, User]` - хранящий всех подключенных и подтвержденных клиентов

`online` - словарь, где ключами являются
уникальные id клиентов (не пользователей),
а значениями объекты User которые представляют пользователя.
Пока пользователь не подтвержден (не авторизован)
объект `User` хранит только собственный объект сокета (`WebServerSocketProtocol`).
При авторизации можно добавить поле `User.id` и `User.token`
хранящие id пользователя (не клиента) и токен доступа сообветственно.

##### Пример

Подключимся через 2 разные вкладки терминала к серверу
и отправим сообщение от одного клиента другому

```python
import asyncio
from uuid import UUID

from pydantic import BaseModel
from websockets import WebSocketServerProtocol

from websuckets import WebSuckets, CommandGroup, ClientEvent
from websuckets.exc import InternalError
from websuckets.session import Session

app = WebSuckets()
group = CommandGroup()


class MessageModel(BaseModel):
    to: UUID
    text: str


@group.command("send message", protected=False)
async def send_message(socket: WebSocketServerProtocol, model: MessageModel):
    my_socket_id = socket.id # id текущего пользователя
    him_socket_id = model.to # id клиента получателя
    if him_socket_id not in Session.online: # если клиент получателя не найден
        raise InternalError("такой клиент не подключен") # выбрасываем ошибку, которая отправиться клиенту
    him_socket = Session.online[him_socket_id].socket # сокет получателя
    author_client_event = ClientEvent(
        event="message sent"
    ) # это сообщение мы отправим отправителю
    receiver_client_event = ClientEvent(event="incoming message",
                                        payload=dict(
                                            author=str(my_socket_id),
                                            text=model.text
                                        )) # это сообщение отправим получателю
    await socket.send(author_client_event) # отправляем отправителю
    await him_socket.send(receiver_client_event) # отправляем получателю


app.include_command_group(group)

app = WebSuckets()
if __name__ == '__main__':
    asyncio.run(app("localhost", 9000))

```
Здесь есть две новые сущности:

`InternalError` - объект ошибки принимающий название ошибки и детали.
если ошибка произошла на запущеном сервере то она отправится клиенту в 
виде JSON. В противном случае она отобразится в консоли сервера (будет изменено в следующих версиях).

`ClientEvent` - функция преобразующая ответ в json с полями 
`event` и `payload` для клиента, по аналогии команд для сервера.
По этому принципу можно будет строить клиент с стандартизированными запросами - ответами,
где клиент может так же реагировать на события по имени как и сервер.

### Приватные (защищенные) команды и верификация пользователя

Команду можно объявить как защищенную, тогда в запросе
обязательно нужно передать поле `token`.
 
###### На примере должно быть понятнее

Напишем программу с тремя командами:

* регистрация пользователя
* аутентификация пользователя
* получение списка пользователей

```python
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

```

Запустим сервер

`python main.py` 

и создадим клиент:

`python -m websockets ws://localhost:9000`

Теперь создадим пользователя 

`{"event":"create", "payload": {"login":"athropyne","password":"SecretpaSSword"}}`

Авторизуем пользователя

`{"event":"auth", "payload": {"login":"athropyne","password":"SecretpaSSword"}}` 

Скопируем токен из ответа и вставим в поле `token`

`{"event":"get list", "token": "4d1d55c66857453fa1adae8bcae61e45"}`

И мы получаем список пользователей.

## Будущие изменения:

* Разграничение ошибок на внутренние (будут выводиться в консоль сервера)
и внешние (будут отправляться клиенту)
* Будут добавлены способы хранения сессий и кэша (redis итд)
* (возможно) Расширение обработчиков. Любая сигнатура и анализ типов.
* (возможно) Внедрение зависимостей в обработчики

**Это dev версия, может меняться все без сохранения обратной совместимости**
