import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db
from app.db.models import Scenario, User
from app.main import app

load_dotenv("tests/.env.test")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL не установлен в переменных окружения.")

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine)

@pytest.fixture
def db():
    """Fixture для предоставления тестовой сессии базы данных."""
    with TestSessionLocal() as session:
        yield session

    session.query(User).delete()
    session.query(Scenario).delete()
    session.commit()

@pytest.fixture
def client(db):
    """Fixture для предоставления тестового клиента FastAPI с переопределенной зависимостью get_db."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()