from sqlalchemy import text


def test_db_connection(db):
    """Тест для проверки подключения к тестовой базе данных."""
    result = db.execute(text("SELECT current_database()"))
    database_name = result.scalar()

    assert database_name == "ryadom_test"