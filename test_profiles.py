import httpx
from models import ProfileMeResponse
from conftest import BASE_URL, TIMEOUT
from api_client import ApiClient
import logging


logging.disable(logging.INFO)


# шаблончик
def get_profile(response):
    """Функция извлекает объект 'profile' из JSON-ответа сервера,
    используется для сокращения повторений в коде"""
    return response.json()["profile"]


# Тесты профиля пользователя

def test_user_get_his_profile(user_token):
    """Отправка запроса с токеном пользователя для получения его профиля,
    сервер возвращает статус-код 200"""
    response = ApiClient.get_my_profile(user_token)

    assert response.status_code == 200


def test_user_validation_profile_via_pydantic(user_token):
    """Pydantic проверяет всю структуру ответа"""
    response = ApiClient.get_my_profile(user_token)

    assert response.status_code == 200

    # Если структура не совпадает, то Pydantic возвращает ValidationError и тест падает
    profile = ProfileMeResponse(**response.json())
    assert profile.profile.username != ""


def test_user_profileUsername_match_uresUsername(user_token, user_info):
    """Отправка запроса на получение профиля пользователя,
    проверка username в полученном профиле с username под которым авторизовались"""
    response = ApiClient.get_my_profile(user_token)
    profile = get_profile(response)

    assert profile["username"] == user_info["username"]


def test_user_role_equal_user(user_token):
    """Отправка запроса на получение профиля пользователя,
      проверка, что у обычного пользователя роль 'user'"""
    response = ApiClient.get_my_profile(user_token)
    profile = get_profile(response)

    assert profile["role"]["name"] == "user"


def test_get_profile_withoutatoken_forbiden():
    """Отправка запроса на получение профиля, без токена пользователя,
    сервер возвращает статус-код 403"""
    response = httpx.get(
        f"{BASE_URL}/api/profiles/me",
        timeout=TIMEOUT
    )

    assert response.status_code == 403

    # Валидация текста ошибки — проверка, возвращает ли сервер причину из-за которой произошел отказ
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0


# Тест профиля администратора

def test_admin_get_his_profile(admin_token):
    """Отправка запроса с токеном администратора для получения его профиля,
    сервер возвращает статус-код 200"""
    response = ApiClient.get_my_profile(admin_token)

    assert response.status_code == 200


def test_admin_role_equal_admin(admin_token):
    """Отправка запроса на получение профиля администратора,
      проверка, что у администратора роль 'admin'"""
    response = ApiClient.get_my_profile(admin_token)
    profile = get_profile(response)

    assert profile["role"]["name"] in ("admin", "superadmin")


# Тест списка профилей

def test_admin_display_all_users(admin_token):
    """Отправка запроса под админом на получение списка всех пользователей,
    проверка, что в полученном списке есть пользователи кроме админа"""
    response = ApiClient.get_profiles_list(admin_token)

    assert response.status_code == 200

    data = response.json()
    assert "profiles" in data
    assert "count" in data
    assert data["count"] > 1   # у admin видно больше одного пользователя


def test_user_see_only_his_profile(user_token):
    """Отправка запроса под пользователем на получение списка пользователей,
    проверка, что в полученном списке есть только текущий пользователь"""
    response = ApiClient.get_profiles_list(user_token)

    assert response.status_code == 200

    data = response.json()
    # У обычного пользователя в списке только он сам (или 0 если профиль не создан)
    assert data["count"] <= 1


def test_admin_get_profile_user_by_id(admin_token, user_info):
    """Запрос на получение профиля пользователя администратором по ID,
    проверка, что полученный профиль тот который мы запрашивали:
    сверяем id и username полученного профиля с теми что передавали"""
    response = ApiClient.get_profile_by_id(admin_token, user_info["id"])

    assert response.status_code == 200

    profile = get_profile(response)
    assert profile["id"] == user_info["id"]
    assert profile["username"] == user_info["username"]


def test_user_dontGet_other_profile(user_token, admin_token):
    """Отправка запроса для получения ID администратора,
    отправка запроса на получение профиля админа пользователем,
    сервер возвращает статус-код 403"""
    # Узнаём ID администратора
    admin_response = ApiClient.get_my_profile(admin_token)
    admin_id = get_profile(admin_response)["id"]

    # Пробуем получить профиль admin от имени обычного user
    response = ApiClient.get_profile_by_id(user_token, admin_id)

    assert response.status_code == 403


    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0
