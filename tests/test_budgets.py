from datetime import datetime
from decimal import Decimal

import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data):
    return client.post(
        path,
        data={**data, "csrf_token": "test-csrf-token"},
        follow_redirects=False,
    )


def _add_category(db_query, name):
    db_query(
        "INSERT INTO categories (name, description) VALUES (%s, 'Budget test category')",
        (name,),
        fetch="none",
    )
    return db_query("SELECT id FROM categories WHERE name=%s", (name,))[0]


def _add_budget(db_query, category_id, month, amount):
    db_query(
        """
        INSERT INTO category_budgets (category_id, month, amount, created_by, updated_by)
        VALUES (%s, %s, %s, 'admin_test', 'admin_test')
        """,
        (category_id, month, amount),
        fetch="none",
    )


def _add_record(db_query, concept, amount, month, record_type, category_id):
    db_query(
        """
        INSERT INTO records (concept, amount, date, type, category_id, created_by)
        VALUES (%s, %s, %s, %s, %s, 'admin_test')
        """,
        (concept, amount, month, record_type, category_id),
        fetch="none",
    )


def test_all_fixture_categories_have_a_budget(db_query):
    assert db_query("SELECT COUNT(*) FROM categories")[0] == 3
    assert db_query(
        """
        SELECT COUNT(*)
        FROM categories c
        JOIN category_budgets b ON b.category_id=c.id AND b.month='2026-07'
        """
    )[0] == 3


def test_budget_summary_uses_all_budgeted_categories(admin_client):
    response = admin_client.get("/budgets?month=2026-07")
    assert response.status_code == 200
    assert b"3.000,00" in response.data
    assert b"1.334,56" in response.data
    assert b"1.665,44" in response.data


def test_budget_counts_all_expenses_regardless_of_funding_account(admin_client, db_query):
    category_id = _add_category(db_query, "Risk test")
    _add_budget(db_query, category_id, "2026-07", 1000)
    _add_record(db_query, "Counted expense", 800, "2026-07", "expense", category_id)
    _add_record(db_query, "Saving expense", 500, "2026-07", "expense", category_id)
    _add_record(db_query, "Ignored income", 900, "2026-07", "income", category_id)
    _add_record(db_query, "Ignored saving", 700, "2026-07", "saving", category_id)
    _add_record(db_query, "Other month", 600, "2026-06", "expense", category_id)

    response = admin_client.get("/budgets?month=2026-07")
    assert response.status_code == 200
    marker = f'data-category-id="{category_id}"'.encode()
    start = response.data.index(marker)
    row = response.data[start:start + 1200]
    assert b'data-budget-state="exceeded"' in row
    assert b'data-spent="1300.00"' in row
    assert b'data-percentage="130.0"' in row


def test_budget_filters_risk_exceeded_and_unbudgeted(admin_client, db_query):
    exceeded_id = _add_category(db_query, "Exceeded test")
    _add_budget(db_query, exceeded_id, "2026-07", 100)
    _add_record(db_query, "Exceeded expense", 110, "2026-07", "expense", exceeded_id)
    unbudgeted_id = _add_category(db_query, "Unbudgeted test")

    risk = admin_client.get("/budgets?month=2026-07&status=risk")
    assert b"Exceeded test" in risk.data
    assert b'data-category-id="1"' in risk.data
    assert b'data-category-id="2"' not in risk.data

    exceeded = admin_client.get("/budgets?month=2026-07&status=exceeded")
    assert b"Exceeded test" in exceeded.data
    assert b'data-category-id="1"' not in exceeded.data

    unbudgeted = admin_client.get("/budgets?month=2026-07&status=unbudgeted")
    assert f'data-category-id="{unbudgeted_id}"'.encode() in unbudgeted.data
    assert f'data-category-id="{exceeded_id}"'.encode() not in unbudgeted.data


def test_latest_effective_budget_is_inherited(admin_client, db_query):
    category_id = _add_category(db_query, "Inherited test")
    _add_budget(db_query, category_id, "2026-06", 420)

    response = admin_client.get("/budgets?month=2026-07")
    marker = f'data-category-id="{category_id}"'.encode()
    start = response.data.index(marker)
    row = response.data[start:start + 1200]
    assert b"420,00" in row
    assert f"/budgets/{category_id}/save".encode() in response.data


def test_editing_current_budget_preserves_history(admin_client, db_query):
    _add_budget(db_query, 2, "2026-06", 250)
    _post(admin_client, "/budgets/2/save", {"month": "2026-06", "amount": "1200"})

    values = db_query(
        "SELECT month, amount FROM category_budgets WHERE category_id=2 ORDER BY month",
        fetch="all",
    )
    assert values == [
        ("2026-06", Decimal("250.00")),
        ("2026-07", Decimal("1200.00")),
    ]

    history = admin_client.get("/budgets?month=2026-06")
    assert b"250,00" in history.data
    assert b"/budgets/2/save" not in history.data


def test_remove_budget_keeps_history_and_marks_current_month_unbudgeted(admin_client, db_query):
    _add_budget(db_query, 2, "2026-06", 250)

    response = _post(admin_client, "/budgets/2/remove", {})
    assert response.status_code in {302, 303}
    assert db_query(
        """
        SELECT amount, is_disabled
        FROM category_budgets
        WHERE category_id=2 AND month='2026-07'
        """
    ) == (None, True)

    current = admin_client.get("/budgets?month=2026-07&status=unbudgeted")
    assert b'data-category-id="2"' in current.data
    assert b'data-budget-state="unbudgeted"' in current.data

    history = admin_client.get("/budgets?month=2026-06")
    assert b"250,00" in history.data
    assert b'data-category-id="2"' in history.data


def test_removed_budget_can_be_assigned_again(admin_client, db_query):
    _post(admin_client, "/budgets/2/remove", {})
    _post(admin_client, "/budgets/2/save", {"amount": "1200"})

    assert db_query(
        """
        SELECT amount, is_disabled
        FROM category_budgets
        WHERE category_id=2 AND month='2026-07'
        """
    ) == (Decimal("1200.00"), False)


def test_dashboard_excludes_removed_budget(admin_client):
    _post(admin_client, "/budgets/2/remove", {})

    response = admin_client.get("/?month=2026-07")
    assert response.status_code == 200
    assert b"2.000,00" in response.data
    assert b"3.000,00" not in response.data


def test_demo_seed_forces_all_categories_and_clear_restores_previous_state(admin_client, db_query, monkeypatch):
    import routes.budgets

    monkeypatch.setattr(routes.budgets, "datetime", datetime)
    current_month = datetime.now().strftime("%Y-%m")
    new_category_id = _add_category(db_query, "Demo uncovered test")
    _post(admin_client, "/budgets/1/remove", {})

    _post(admin_client, "/management/demo-data/seed", {})

    uncovered = db_query(
        """
        SELECT COUNT(*)
        FROM categories c
        LEFT JOIN LATERAL (
            SELECT amount, is_disabled
            FROM category_budgets b
            WHERE b.category_id=c.id AND b.month <= %s
            ORDER BY b.month DESC
            LIMIT 1
        ) budget ON TRUE
        WHERE budget.amount IS NULL OR budget.is_disabled=TRUE
        """,
        (current_month,),
    )[0]
    assert uncovered == 0
    assert db_query(
        "SELECT amount, is_disabled, updated_by FROM category_budgets WHERE category_id=1 AND month=%s",
        (current_month,),
    )[1:] == (False, "[DEMO_SEED_MANAGEMENT]")
    assert db_query(
        "SELECT created_by FROM category_budgets WHERE category_id=%s AND month=%s",
        (new_category_id, current_month),
    )[0] == "[DEMO_SEED_MANAGEMENT]"

    _post(admin_client, "/management/demo-data/clear", {})

    assert db_query(
        "SELECT amount, is_disabled FROM category_budgets WHERE category_id=1 AND month=%s",
        (current_month,),
    ) == (None, True)
    assert db_query(
        "SELECT COUNT(*) FROM category_budgets WHERE category_id=%s",
        (new_category_id,),
    )[0] == 0


def test_future_month_is_clamped_to_current_month(admin_client):
    response = admin_client.get("/budgets?month=2099-12")
    assert response.status_code == 200
    assert b'value="2026-07"' in response.data
    assert b"Mes actual" in response.data


@pytest.mark.parametrize("amount", ["", "0", "-1", "not-a-number", "10000000000"])
def test_invalid_budget_amount_is_rejected(admin_client, db_query, amount):
    response = _post(admin_client, "/budgets/2/save", {"amount": amount})
    assert response.status_code in {302, 303}
    assert "error=".encode() in response.headers["Location"].encode()
    assert db_query(
        "SELECT amount FROM category_budgets WHERE category_id=2 AND month='2026-07'"
    )[0] == Decimal("1000.00")


def test_dashboard_uses_effective_budget_and_counts_exceeded_categories(admin_client, db_query):
    db_query(
        "UPDATE category_budgets SET amount=1000 WHERE category_id=1 AND month='2026-07'",
        fetch="none",
    )
    response = admin_client.get("/?month=2026-07")
    assert response.status_code == 200
    assert b"3.000,00" not in response.data
    assert b"2.500,00" in response.data
    assert b"1.334,56" in response.data
    assert "1 categorías excedidas".encode() in response.data
