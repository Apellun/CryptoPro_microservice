class CryptoApiError(Exception):
    def __init__(self, message: str = "Ошибка работы API",
                 name: str = "Crypto API", details: str = ""):
        self.message = message
        self.name = name
        self.details = details
        super().__init__(self.message, self.name)


class UniqueConstraintError(CryptoApiError):
    def __init__(self, details: str = "", message: str = "Объект с подобным значением поля уже существует в базе"):
        super().__init__(message=message, details=details)


class DatabaseError(CryptoApiError):
    def __init__(self, details: str = ""):
        super().__init__(details=details)


class EntityNotFoundError(CryptoApiError):
    def __init__(self, details: str = "", message: str = "Объект не найден"):
        super().__init__(message=message, details=details)