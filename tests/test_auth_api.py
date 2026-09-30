from app.db.models import Scenario, User


def test_register_user(client, db):
    """Тест для проверки регистрации нового пользователя через API."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Тестовый пользователь",
            "age": 30,
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Тестовый пользователь"
    assert data["age"] == 30
    assert data["email"] == "test@example.com"

    user = db.query(User).filter(User.email == "test@example.com").first()

    assert user is not None
    assert user.name == "Тестовый пользователь"
    assert user.password_hash != "password123"

def test_register_duplicate_email(client, db):
    """Тест для проверки регистрации пользователя с уже существующим email."""
    user_data = {
        "name": "Первый пользователь",
        "age": 30,
        "email": "duplicate@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Пользователь с таким email уже существует"
    )

def test_register_invalid_age(client):
    """Тест для проверки регистрации пользователя с недопустимым возрастом."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Тест",
            "age": 15,
            "email": "invalid-age@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 422

def test_login_user(client):
    """Тест для проверки успешного входа пользователя через API."""
    user_data = {
        "name": "Тестовый пользователь",
        "age": 30,
        "email": "login@example.com",
        "password": "password123",
    }

    register_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

def test_login_wrong_password(client):
    """Тест для проверки входа пользователя с неверным паролем через API."""
    user_data = {
        "name": "Тестовый пользователь",
        "age": 30,
        "email": "wrong-password@example.com",
        "password": "password123",
    }

    register_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": "wrong-password",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Неверный email или пароль"

def test_login_nonexistent_email(client):
    """Тест для проверки входа пользователя с несуществующим email через API."""

    login_response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent_email@example.com",
            "password": "password123",
        }
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Неверный email или пароль"

def test_get_current_user(client):
    """Тест для проверки получения текущего пользователя через API."""
    user_data = {
            "name": "Тестовый пользователь",
            "age": 30,
            "email": "current_user@example.com",
            "password": "password123",
        }

    register_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    current_user_response = client.get(
        "/users/me",
        headers=headers,
    )

    assert current_user_response.status_code == 200
    assert current_user_response.json()["name"] == user_data["name"]
    assert current_user_response.json()["age"] == user_data["age"]

def test_get_current_user_without_token(client):
    """Тест для проверки получения текущего пользователя без токена через API."""
    current_user_response = client.get("/users/me")

    assert current_user_response.status_code == 401
    assert current_user_response.json()["detail"] == "Not authenticated"

def test_get_current_user_invalid_token(client):
    """Тест для проверки получения текущего пользователя с недействительным токеном через API."""
    headers = {"Authorization": "Bearer invalid_token"}

    current_user_response = client.get(
        "/users/me",
        headers=headers,
    )

    assert current_user_response.status_code == 401
    assert current_user_response.json()["detail"] == "Неверный токен"

def test_recommendations_endpoint_with_scenario(client, db):
    """Тестирование получения рекомендации из базы данных."""

    scenario = Scenario(
        category="tantrum",
        subcategory="denied_request",
        age_min=2,
        age_max=6,
        place=None,
        title="Ребёнок сильно расстроился из-за отказа",
        steps=[
            "Сохраняйте спокойствие и говорите коротко.",
            "Назовите эмоцию ребёнка спокойными словами.",
        ],
        phrase="Я вижу, что ты очень расстроился. Ты хотел это получить. Я рядом.",
        avoid=["Не кричите в ответ."],
        if_not_helped="Дайте ребёнку немного времени успокоиться.",
        is_active=True,
    )

    db.add(scenario)
    db.commit()

    response = client.post(
        "/recommendations",
        json={
            "age": 4,
            "category": "tantrum",
            "subcategory": "denied_request",
            "place": "home",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Ребёнок сильно расстроился из-за отказа"
    assert data["steps"] == [
        "Сохраняйте спокойствие и говорите коротко.",
        "Назовите эмоцию ребёнка спокойными словами.",
    ]
    assert data["phrase"] == (
        "Я вижу, что ты очень расстроился. Ты хотел это получить. Я рядом."
    )