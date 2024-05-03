class ServerConnectionError(Exception):
    def __init__(self):
        message = "Ошибка подключения к серверу."
        super().__init__(message)


class EmptyResponseError(Exception):
    def __init__(self):
        message = "Сервер не вернул ответ."
        super().__init__(message)


class ResponseCodeError(Exception):
    def __init__(self, code, response_message):
        message = f"Неправильный запрос к серверу:\n{code}:{response_message}."
        super().__init__(message)


class InternalServerError(Exception):
    def __init__(self):
        message = f"Внутренняя ошибка сервера."
        super().__init__(message)


class OrgDataIntegrityError(Exception):
    def __init__(self, message):
        super().__init__(message)