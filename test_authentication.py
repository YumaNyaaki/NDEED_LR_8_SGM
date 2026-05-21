import pytest
import httpx
from models import TokenResponse
from conftest import BASE_URL, TIMEOUT, ADMIN_USERNAME, ADMIN_PASSWORD
from api_client import ApiClient
import logging


logging.disable(logging.INFO)


# Тест 1: авторизация с правильными данными

def test_login_corret_autorisation(user_info):
    """Отправка корректных имени пользователя и пароля,
     проверка на возврат сервером токена пользователя"""
    response = ApiClient.login(user_info["username"], user_info["password"])

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_login_correct_structure_responce(user_info):
    """Pydantic проверяет что в ответе есть access_token и token_type
    Необходимо для того, чтобы проверить правильность всей структуры ответа от сервера,
    т.к. если тип будет отличатся от необходимого, то остальные запросы работать не будут"""
    response = ApiClient.login(user_info["username"], user_info["password"])

    assert response.status_code == 200

    # Pydantic вернет ошибку если один из токенов не будет получен или будет не того типа
    token_data = TokenResponse(**response.json())
    assert token_data.token_type.lower() == "bearer"


# Тест 2: использование неправильных данных

def test_login_incorrect_password(user_info):
    """Отправка запроса с неправильно указанным паролем,
     сервер возвращает статус-код 401"""
    response = ApiClient.login(user_info["username"], "incorrect_test_pass_123")

    assert response.status_code == 401

    # Валидация текста ошибки — проверка, возвращает ли сервер причину из-за которой произошел отказ
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0


def test_login_fake_username(user_info):
    """Отправка на сервер запроса с несуществующим именем пользователя,
     сервер возвращает статус-код 401"""
    response = ApiClient.login("Slyusarev_fake", user_info["password"])

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0


def test_login_blank_body_request():
    """Отправка пустого тела запроса на сервер,
     сервер возвращает статус-код 422"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={},
        timeout=TIMEOUT
    )

    assert response.status_code == 422

    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)


# Тест 3: верификация токена пользователя

def test_verify_correct_token(user_token):
    """Отправка правильного токена,
     сервер возвращает статус-код 200"""
    response = ApiClient.verify_token(user_token)

    assert response.status_code == 200


def test_verify_fake_token():
    """Отправка не правильного токена,
     сервер возвращает статус-код 401"""
    response = ApiClient.verify_token("token_99_pocentov_pravilny")

    assert response.status_code == 401


    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0


def test_verify_blank():
    """Отправка запроса без токена,
     сервер возвращает статус-код 403"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/verify",
        timeout=TIMEOUT
    )

    assert response.status_code == 403


# Тест 4: смена пароля

def test_replacement_password(user_info, user_token):
    """Отправка запроса смены пароля, проверка возможности входа с новым паролем
     путем отправки запроса авторизации"""
    new_password = "new_test_pass_123"

    # Меняем пароль
    change_response = ApiClient.change_password(user_token, user_info["password"], new_password)
    assert change_response.status_code == 200

    # Проверяем что с новым паролем можно войти
    login_response = ApiClient.login(user_info["username"], new_password)
    assert login_response.status_code == 200


# Тест: 5 тест входа для разных ролей

@pytest.mark.parametrize("username, password, expected_role", [
    ("admin", "admin123", "admin"),
    ("user", "user123", "user"),
    ("moderator", "moderator123", "moderator"),
])
def test_login_different_roles(username, password, expected_role):
    """Отправка запроса авторизации для пользователей с разными ролями,
    проверка, что каждый из них получает токен и его роль соответствует ожидаемой"""
    response = ApiClient.login(username, password)

    assert response.status_code == 200, f"Не удалось войти как {expected_role}"

    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0

    # Достаём роль из токена — она хранится прямо внутри него в открытом виде
    # Токен выглядит как "часть1.часть2.часть3", нас интересует вторая часть
    import base64, json
    payload_b64 = data["access_token"].split(".")[1]
    # base64 требует длину кратную 4, добавляем padding
    payload_b64 += "=" * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.b64decode(payload_b64))
    assert payload["role"] == expected_role
