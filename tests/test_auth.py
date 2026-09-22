import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest


def test_register_request_valid():
    user = RegisterRequest(
        name="Игорь",
        age=33,
        email="test@example.com",
        password="password123",
    )

    assert user.name == "Игорь"
    assert user.age == 33
    assert user.email == "test@example.com"


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "age": 33, "email": "test@example.com", "password": "password123"},
        {
            "name": "A" * 101,
            "age": 33,
            "email": "test@example.com",
            "password": "password123",
        },
        {
            "name": "Игорь",
            "age": 17,
            "email": "test@example.com",
            "password": "password123",
        },
        {
            "name": "Игорь",
            "age": 121,
            "email": "test@example.com",
            "password": "password123",
        },
        {
            "name": "Игорь",
            "age": 33,
            "email": "test@example.com",
            "password": "1234567",
        },
        {"name": "Игорь", "age": 33, "email": "not-email", "password": "password123"},
    ],
)
def test_register_request_invalid(data):
    with pytest.raises(ValidationError):
        RegisterRequest(**data)
