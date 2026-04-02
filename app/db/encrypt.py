import base64, hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class EncryptData:
    """Класс для работы с шифрованием данных"""
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Создать новый Argon2-хеш"""
        return self.ph.hash(password)

    def verify_password(self, stored_hash: str, password: str) -> tuple[bool, str | None]:
        """
        Проверяет пароль.
        Возвращает (is_valid, new_hash).
        Если is_valid=True и new_hash не None -> нужно обновить хеш в базе.
        """
        if stored_hash.startswith("$argon2"):  # уже Argon2
            try:
                self.ph.verify(stored_hash, password)
                if self.ph.check_needs_rehash(stored_hash):
                    # пароль верный, но параметры устарели — пересчитаем
                    return True, self.ph.hash(password)
                return True, None
            except VerifyMismatchError:
                return False, None

        elif stored_hash.startswith("scrypt:"):  # старый формат
            try:
                algo, params, salt_b64, hash_hex = stored_hash.split("$")
                n, r, p = map(int, params.split(":"))
                salt = base64.b64decode(salt_b64)
                dk = hashlib.scrypt(
                    password.encode(),
                    salt=salt,
                    n=n, r=r, p=p,
                    dklen=len(bytes.fromhex(hash_hex))
                )
                if dk.hex() == hash_hex:
                    # пароль верный, пересчитаем в Argon2
                    return True, self.ph.hash(password)
                return False, None
            except Exception:
                return False, None

        else:
            # неизвестный формат
            return False, None
