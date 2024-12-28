from brom import *


def create_client(url, database, username, password):
    """
    Creates and returns a БромКлиент object.
    """
    try:
        return БромКлиент(
            публикация=f"{url}/{database}",
            пользователь=username,
            пароль=password,
        )
    except Exception as error:
        print("Ошибка создания клиента:", error)