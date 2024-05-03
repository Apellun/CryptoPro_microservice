class DBException(Exception):
    def __init__(self):
        self.message = "Ошибка Базы Данных."
        super().__init__(self.message)


class IntegrityException(Exception):
    def __init__(self):
        self.message = "Организация с таким ИНН или названием уже существует в базе."
        super().__init__(self.message)