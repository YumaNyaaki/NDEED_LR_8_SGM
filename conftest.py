import pytest
import httpx
import random
import logging


BASE_URL = "https://secby.ru"
TIMEOUT = 10.0 #интернет часто лагает поэтому такой большой таймаут

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные авторизации админки
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def random_suffix():
    return random.randint(111, 111111)


# Токен админа за тестовую сессию создается 1 раз
@pytest.fixture(scope="session")
def admin_token():
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT
    )
    assert response.status_code == 200, "Не удалось войти как администратор"
    return response.json()["access_token"]


# Создаём тестового пользователя для каждого теста
@pytest.fixture()
def user_info(admin_token):
    suffix = random_suffix()
    payload = {
        "username": f"user_Slyusarev_Autotest_{suffix}",
        "email": f"user_Slyusarev_Autotest_{suffix}@mylo.com",
        "password": "test_pass123"
    }

    # Регистрируем этого пользователя
    reg_response = httpx.post(
        f"{BASE_URL}/api/auth/register",
        json=payload,
        timeout=TIMEOUT
    )
    assert reg_response.status_code in (200, 201), "Не удалось зарегистрировать пользователя"

    user_id = reg_response.json()["account"]["id"]

    yield {
        "id": user_id,
        "username": payload["username"],
        "password": payload["password"]
    }

    # Удаляем пользователя после выполнения
    headers = {"Authorization": f"Bearer {admin_token}"}
    httpx.delete(
        f"{BASE_URL}/api/profiles/{user_id}",
        headers=headers,
        timeout=TIMEOUT
    )


# Токен тестового пользователя
@pytest.fixture()
def user_token(user_info):
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_info["username"], "password": user_info["password"]},
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    return response.json()["access_token"]
