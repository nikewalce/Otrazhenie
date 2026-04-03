class ValidationError(Exception):
    """Простое исключение валидации для сервиса"""

    def __init__(self, errors):
        super().__init__("Ошибка валидации")
        self.errors = errors
