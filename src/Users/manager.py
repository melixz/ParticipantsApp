from argon2 import PasswordHasher


class UserHashManager:
    def __init__(self, ph=PasswordHasher()):
        self.ph = ph

    def hash_password(self, password: str) -> str:
        """Создает хэш пароля."""
        return self.ph.hash(password)

    def check_password(self, stored_hashed_password: str, input_password: str) -> bool:
        """Проверяет соответствие хэша и введенного пароля."""
        try:
            return self.ph.verify(stored_hashed_password, input_password)
        except Exception:
            return False


user_hash_manager = UserHashManager()
