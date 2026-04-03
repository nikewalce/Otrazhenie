import re


class UserRegistrationSchema:
    required_fields = ["username", "email", "password"]

    EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"

    def validate(self, data: dict) -> dict:
        errors = {}
        for field in self.required_fields:
            if field not in data or not data[field]:
                errors[field] = f"{field} обязательное поле"

        # Строгая проверка email
        if "email" in data and not re.match(self.EMAIL_REGEX, data["email"]):
            errors["email"] = "Некорректный email"

        if "username" in data and len(data["username"]) < 3:
            errors["username"] = "Имя пользователя должно быть не менее 3 символов"
        return errors

    def load(self, data: dict) -> dict:
        return {k: data[k] for k in self.required_fields if k in data}
