import httpx
from conftest import BASE_URL, TIMEOUT


class ApiClient:
    """Класс для работы с API, нужен чтобы убрать повторения из тестов"""

    # Аутентификация

    @staticmethod
    def login(username, password):
        """Отправка запроса авторизации"""
        return httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT
        )

    @staticmethod
    def register(username, email, password):
        """Отправка запроса регистрации"""
        return httpx.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=TIMEOUT
        )

    @staticmethod
    def verify_token(token):
        """Отправка запроса верификации токена"""
        return httpx.post(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT
        )

    @staticmethod
    def change_password(token, old_password, new_password):
        """Отправка запроса смены пароля"""
        return httpx.post(
            f"{BASE_URL}/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"old_password": old_password, "new_password": new_password},
            timeout=TIMEOUT
        )

    # Профили пользователя

    @staticmethod
    def get_my_profile(token):
        """Получение профиля текущего пользователя"""
        return httpx.get(
            f"{BASE_URL}/api/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT
        )

    @staticmethod
    def get_profile_by_id(token, user_id):
        """Получение профиля пользователя по ID"""
        return httpx.get(
            f"{BASE_URL}/api/profiles/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT
        )

    @staticmethod
    def get_profiles_list(token):
        """Получение списка всех профилей"""
        return httpx.get(
            f"{BASE_URL}/api/profiles/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT
        )

    @staticmethod
    def delete_profile(token, user_id):
        """Удаление профиля пользователя"""
        return httpx.delete(
            f"{BASE_URL}/api/profiles/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT
        )
