import httpx
from models import TokenResponse
from conftest import BASE_URL, TIMEOUT, ADMIN_USERNAME, ADMIN_PASSWORD
import logging


logging.disable(logging.INFO)


# Тест 1: авторизация с правильными данными

def test_login_corret_autorisation(user_info):
    """Отправка корректных имени пользователя и пароля,
     проверка на возврат сервером токена пользователя"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_info["username"], "password": user_info["password"]},
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_login_correct_structure_responce(user_info):
    """Pydantic проверяет что в ответе есть access_token и token_type
    Необходимо для того, чтобы проверить правильность всей структуры ответа от сервера,
    т.к. если тип будет отличатся от необходимого, то остальные запросы работать не будут"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_info["username"], "password": user_info["password"]},
        timeout=TIMEOUT
    )

    assert response.status_code == 200

    # Pydantic вернет ошибку если один из токенов не будет получен или будет не того типа
    token_data = TokenResponse(**response.json())
    assert token_data.token_type.lower() == "bearer"


# Тест 2: использование неправильных данных

def test_login_incorrect_password(user_info):
    """Отправка запроса с неправильно указанным паролем,
     сервер возвращает статус-код 401"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_info["username"], "password": "incorrect_test_pass_123"},
        timeout=TIMEOUT
    )

    assert response.status_code == 401


def test_login_fake_username(user_info):
    """Отправка на сервер запроса с несуществующим именем пользователя,
     сервер возвращает статус-код 401"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "Slyusarev_fake", "password": user_info["password"]},
        timeout=TIMEOUT
    )

    assert response.status_code == 401


def test_login_blank_body_request():
    """Отправка пустго тела запроса на сервер,
     сервер возвращает статус-код 422"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={},
        timeout=TIMEOUT
    )

    assert response.status_code == 422


# Тест 3: верификация токена пользователя

def test_verify_correct_token(user_token):
    """Отправка правильного токена,
     сервер возвращает статус-код 200"""
    headers = {"Authorization": f"Bearer {user_token}"}

    response = httpx.post(
        f"{BASE_URL}/api/auth/verify",
        headers=headers,
        timeout=TIMEOUT
    )

    assert response.status_code == 200


def test_verify_fake_token():
    """Отправка не правильного токена,
     сервер возвращает статус-код 401"""
    headers = {"Authorization": "Bearer token_99_pocentov_pravilny"}

    response = httpx.post(
        f"{BASE_URL}/api/auth/verify",
        headers=headers,
        timeout=TIMEOUT
    )

    assert response.status_code == 401


def test_verify_blank():
    """Отправка запроса без токена,
     сервер возвращает статус-код 403"""
    response = httpx.post(
        f"{BASE_URL}/api/auth/verify",
        timeout=TIMEOUT
    )

    assert response.status_code ==  403


# Тест 4 смена пароля

def test_replacement_password(user_info, user_token):
    """Отправка запроса смены пароля, проверка возможности входа с новым паролем
     путем отправки запроса авторизации"""
    headers = {"Authorization": f"Bearer {user_token}"}
    new_password = "new_test_pass_123"

    # Меняем пароль
    change_response = httpx.post(
        f"{BASE_URL}/api/auth/change-password",
        headers=headers,
        json={"old_password": user_info["password"], "new_password": new_password},
        timeout=TIMEOUT
    )
    assert change_response.status_code == 200

    # Проверяем что с новым паролем можно войти
    login_response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_info["username"], "password": new_password},
        timeout=TIMEOUT
    )
    assert login_response.status_code == 200



