# employees/tests/conftest.py
import pytest
from django.db import connection
from django.test import override_settings

@pytest.fixture(autouse=True)
@override_settings(ROOT_URLCONF="employees.urls")
def _urls():
    """Підміняємо роутинг на urls саме цього app під час тестів (зручно для інтеграційних)."""
    yield

@pytest.fixture(autouse=True)
def _schema():
    """
    На кожен тест створюємо мінімально необхідні таблиці
    (positions, employees) і після - дропаємо.
    """
    with connection.cursor() as c:
        # дропаєм на випадок попередніх запусків
        c.execute("DROP TABLE IF EXISTS employees;")
        c.execute("DROP TABLE IF EXISTS positions;")

        c.execute("""
            CREATE TABLE positions(
                id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                title TEXT NOT NULL,
                category TEXT NOT NULL
            );
        """)
        c.execute("""
            CREATE TABLE employees(
                id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                first_name TEXT NOT NULL,
                last_name  TEXT NOT NULL,
                father_name TEXT,
                birthday TEXT,
                start_date TEXT,
                end_date   TEXT,
                salary REAL NOT NULL,
                position_id INTEGER NOT NULL,
                category TEXT NOT NULL
            );
        """)
        c.executemany(
            "INSERT INTO positions(title, category) VALUES(%s, %s)",
            [
                ("Головний інженер", "Інженерно-технічний персонал"),
                ("Начальник дільниці", "Інженерно-технічний персонал"),
                ("Муляр", "Робітники"),
                ("Електрик", "Робітники"),
            ],
        )
    yield
    with connection.cursor() as c:
        c.execute("DROP TABLE IF EXISTS employees;")
        c.execute("DROP TABLE IF EXISTS positions;")

@pytest.fixture
def positions_ids():
    """Повертає словник {назва: id} - щоб зручно підставляти у форми."""
    with connection.cursor() as c:
        c.execute("SELECT id, title FROM positions;")
        rows = c.fetchall()
    return {title: pid for (pid, title) in rows}
