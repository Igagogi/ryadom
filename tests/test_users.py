from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_users():
    """Тестирование эндпоинта получения всех пользователей."""
    response = client.get("/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
