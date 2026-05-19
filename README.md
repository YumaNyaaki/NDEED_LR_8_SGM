# Основы автоматизации тестирования (практическая работа 8)

Набор автотестов для проверки API сайта "Заметница" `https://secby.ru`.

## Стек

- **Python 3.14**
- **pytest** — фреймворк для запуска тестов
- **httpx** — HTTP-клиент для отправки запросов
- **pydantic** — валидация структуры ответов сервера

## Структура проекта

```
indeed_QA/
├── conftest.py          # Фикстуры: admin_token, user_info, user_token
├── models.py            # Pydantic-модели для валидации ответов API
├── test_auth.py         # Тесты аутентификации и работы с токенами
├── test_profiles.py     # Тесты профилей пользователей и ролевой модели
└──requirements.txt     # Зависимости проекта
```

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Запуск тестов

```bash
pytest                        # все тесты
pytest testy_autentifikacii.py           # только тесты аутентификации
pytest testy_profilej.py       # только тесты профилей
pytest -v                     # с подробным выводом
```

## Описание тестов

### `testy_autentifikacii.py` — Аутентификация

| Тест | Описание                                   |
|------|--------------------------------------------|
| `test_login_corret_autorisation` | Авторизация, получение токена              |
| `test_login_correct_structure_responce` | Структура ответа соответствует схеме       |
| `test_login_incorrect_password` | Неверный пароль                            |
| `test_login_fake_username` | Несуществующий пользователь                |
| `test_login_blank_body_request` | Пустое тело запроса                        |
| `test_verify_correct_token` | Запрос с использованием правильного токена |
| `test_verify_fake_token` | Запрос с непровильным токена               |
| `test_verify_blank` | Запрос без токена                          |
| `test_replacement_password` | Смена пароля и вход с новым паролем        |

### `testy_profilej.py` — Профили и роли

| Тест | Описание |
|------|----------|
| `test_user_get_his_profile` | Пользователь получает свой профиль |
| `test_user_validation_profile_via_pydantic` | Структура профиля праильная |
| `test_user_profileUsername_match_uresUsername` | Username в профиле совпадает с username для входа |
| `test_user_role_equal_user` | У обычного пользователя роль `user` |
| `test_get_profile_withoutatoken_forbiden` | Запрос профиля пользователя без токена |
| `test_admin_get_his_profile` | Администратор получает свой профиль |
| `test_admin_role_equal_admin` | У администратора роль `admin` |
| `test_admin_display_all_users` | Администратор видит всех пользователей |
| `test_user_see_only_his_profile` | Пользователь видит только свой профиль |
| `test_admin_get_profile_user_by_id` | Администратор получает профиль пользователя по ID |
| `test_user_dontGet_other_profile` | Пользователь не может получить чужой профиль |

## Фикстуры (`conftest.py`)

- **`admin_token`** (scope=session) — токен администратора, получается один раз за сессию
- **`user_info`** — создаёт уникального тестового пользователя перед тестом и удаляет его после
- **`user_token`** — токен тестового пользователя

## API

Основной URL: `https://secby.ru`

Основные эндпоинты, покрытые тестами:

- `POST /api/auth/login` — авторизация
- `POST /api/auth/verify` — верификация токена
- `POST /api/auth/change-password` — смена пароля
- `GET /api/profiles/me` — профиль текущего пользователя
- `GET /api/profiles/` — список всех профилей
- `GET /api/profiles/{id}` — профиль по ID