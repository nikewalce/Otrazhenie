from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import logging

logger = logging.getLogger(__name__)


class EncryptData:
    """Класс для работы с шифрованием данных"""

    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Создать новый Argon2-хеш"""
        logger.info("Создан новый Argon2-хеш")
        return self.ph.hash(password)

    def verify_password(
        self, stored_hash: str, password: str
    ) -> tuple[bool, str | None]:
        """
        Проверяет пароль.
        Возвращает (is_valid, new_hash).
        Если is_valid=True и new_hash не None -> нужно обновить хеш в базе.
        """
        if stored_hash.startswith("$argon2"):  # проверка, что Argon2
            try:
                self.ph.verify(stored_hash, password)
                if self.ph.check_needs_rehash(stored_hash):
                    # пароль верный, но параметры устарели — пересчитаем
                    return True, self.ph.hash(password)
                return True, None
            except VerifyMismatchError:
                logger.exception("Введенный пароль не совпадает с тем, что хранится в базе данных!")
                return False, None
        return False, None
