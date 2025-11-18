from unittest.mock import patch
from django.test import Client
from django.urls import reverse
from django.db import connection
from django.http import HttpResponse
import pytest

pytestmark = pytest.mark.django_db


def _count(table: str) -> int:
    with connection.cursor() as c:
        c.execute(f"SELECT COUNT(*) FROM {table};")
        return c.fetchone()[0]


def _get_employee(eid: int):
    with connection.cursor() as c:
        c.execute("""
            SELECT id, first_name, last_name, father_name, birthday, start_date,
                   end_date, salary, position_id, category
            FROM employees
            WHERE id = %s;
        """, [eid])
        r = c.fetchone()
    if not r:
        return None
    keys = ["id", "first_name", "last_name", "father_name", "birthday",
            "start_date", "end_date", "salary", "position_id", "category"]
    return dict(zip(keys, r))


@pytest.fixture
def client():
    return Client()


# 1) index - рендерить positions
@patch("employees.views.render")
def test_index_renders_positions(mock_render, client):
    mock_render.return_value = HttpResponse("ok", status=200)
    resp = client.get(reverse("employees:index"))
    assert resp.status_code == 200
    assert mock_render.called
    _, args, kwargs = mock_render.mock_calls[0]
    context = args[2] if len(args) >= 3 else kwargs.get("context", {})
    assert "positions" in context


# 2) add_employee - валідний сценарій
def test_add_employee_happy_path(client, positions_ids):
    payload = {
        "first_name": "Іван",
        "last_name": "Петренко",
        "father_name": "Сергійович",
        "birthday": "1990-01-01",
        "start_date": "2024-10-01",
        "salary": "25000",
        "position_id": str(positions_ids["Муляр"]),
        "category": "Робітники"
    }
    n_before = _count("employees")
    resp = client.post(reverse("employees:add"), data=payload)
    assert resp.status_code == 302
    assert _count("employees") == n_before + 1


# 3) add_employee - пропущене поле last_name -> render із помилкою
@patch("employees.views.render")
def test_add_employee_missing_required_fields(mock_render, client, positions_ids):
    mock_render.return_value = HttpResponse("ok", status=200)
    payload = {
        "first_name": "Іван",
        "last_name": "",
        "salary": "25000",
        "position_id": str(positions_ids["Муляр"]),
        "category": "Робітники"
    }
    resp = client.post(reverse("employees:add"), data=payload)
    assert resp.status_code == 200
    _, args, kwargs = mock_render.mock_calls[0]
    context = args[2] if len(args) >= 3 else kwargs.get("context", {})
    assert "error_msg" in context


# 4) add_employee - категорія не збігається, але логіка ігнорує категорію
def test_add_employee_position_category_mismatch(client, positions_ids):
    payload = {
        "first_name": "Іван",
        "last_name": "Петренко",
        "salary": "25000",
        "position_id": str(positions_ids["Муляр"]),
        "category": "Інженерно-технічний персонал"  # ігнорується
    }
    n_before = _count("employees")
    resp = client.post(reverse("employees:add"), data=payload)
    # redirect, бо логіка не перевіряє категорію
    assert resp.status_code == 302
    assert _count("employees") == n_before + 1

    # перевірка, що все одно збережено як "Робітники"
    emp = _get_employee(_count("employees"))
    assert emp["category"] == "Робітники"

# 5) detail - 404 для неіснуючого
def test_employee_detail_404_for_missing(client):
    resp = client.get(reverse("employees:detail", args=[999_999]))
    assert resp.status_code == 404

# 6) delete - видаляє працівника
def test_delete_employee(client, positions_ids):
    with connection.cursor() as c:
        c.execute("""
            INSERT INTO employees(first_name, last_name, father_name, birthday, start_date,
                                  end_date, salary, position_id, category)
            VALUES ('Тарас', 'Шевченко', NULL, '1980-01-01', '2020-01-01',
                    NULL, 30000, %s, 'Робітники')
            RETURNING id;
        """, [positions_ids["Муляр"]])
        eid = c.fetchone()[0]

    assert _get_employee(eid) is not None
    resp = client.get(reverse("employees:delete", args=[eid]))
    assert resp.status_code == 302
    assert _get_employee(eid) is None

# 7) edit - бізнес-правила
@pytest.mark.parametrize(
    "category, position_title, expect_error_part",
    [
        ("Робітники", "Головний інженер", "Робітники не можуть"),
        ("Робітники", "Начальник дільниці", "Робітники не можуть"),
        ("Інженерно-технічний персонал", "Муляр", "може мати лише посади"),
        ("Інженерно-технічний персонал", "Електрик", "може мати лише посади"),
    ],
)
@patch("employees.views.render")
def test_edit_employee_business_rules(mock_render, client, positions_ids, category, position_title, expect_error_part):
    mock_render.return_value = HttpResponse("ok", status=200)
    with connection.cursor() as c:
        c.execute("""
            INSERT INTO employees(first_name, last_name, father_name, birthday, start_date,
                                  end_date, salary, position_id, category)
            VALUES ('Олег', 'Коваленко', NULL, '1995-07-10', '2022-05-01',
                    NULL, 22000, %s, 'Робітники')
            RETURNING id;
        """, [positions_ids["Муляр"]])
        eid = c.fetchone()[0]

    payload = {
        "first_name": "Олег",
        "last_name": "Коваленко",
        "father_name": "",
        "birthday": "1995-07-10",
        "start_date": "2022-05-01",
        "end_date": "",
        "salary": "22000",
        "position_id": str(positions_ids[position_title]),
        "category": category
    }
    resp = client.post(reverse("employees:edit", args=[eid]), data=payload)
    assert resp.status_code == 200
    _, args, kwargs = mock_render.mock_calls[0]
    context = args[2] if len(args) >= 3 else kwargs.get("context", {})
    assert "error_msg" in context
    assert expect_error_part in context["error_msg"]


# 8) edit - успішне оновлення
def test_edit_employee_update_success(client, positions_ids):
    with connection.cursor() as c:
        c.execute("""
            INSERT INTO employees(first_name, last_name, father_name, birthday, start_date,
                                  end_date, salary, position_id, category)
            VALUES ('Марко', 'Кириленко', NULL, '1992-03-03', '2021-01-01',
                    NULL, 20000, %s, 'Робітники')
            RETURNING id;
        """, [positions_ids["Муляр"]])
        eid = c.fetchone()[0]

    payload = {
        "first_name": "Марко",
        "last_name": "Кириленко",
        "father_name": "",
        "birthday": "1992-03-03",
        "start_date": "2021-01-01",
        "end_date": "",
        "salary": "21000",
        "position_id": str(positions_ids["Електрик"]),
        "category": "Робітники"
    }
    resp = client.post(reverse("employees:edit", args=[eid]), data=payload)
    assert resp.status_code == 302
    emp = _get_employee(eid)
    assert emp["salary"] == 21000.0
    assert emp["position_id"] == positions_ids["Електрик"]
    assert emp["category"] == "Робітники"