import re
from app.db.models import User

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

        if "password" in data and len(data["password"]) < 6:
            errors["password"] = "Пароль должен быть не менее 6 символов"
        return errors

    def load(self, data: dict) -> dict:
        result = {k: data[k] for k in self.required_fields if k in data}

        if "email" in result:
            result["email"] = result["email"].lower().strip()

        return result

class UserPublicSchema:
    @staticmethod
    def dump(user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }