from decimal import Decimal

import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data):
    return client.post(path, data={**data, "csrf_token": "test-csrf-token"}, follow_redirects=False)


def test_category_create_update_delete_flow(admin_client, db_query):
    _post(admin_client, "/categories/add", {"name": "Release Flow", "description": "Created"})
    category_id = db_query("SELECT id FROM categories WHERE name='Release Flow'")[0]
    _post(
        admin_client,
        f"/categories/{category_id}/update",
        {"name": "Release Flow Updated", "description": "Updated"},
    )
    assert db_query("SELECT description FROM categories WHERE id=%s", (category_id,))[0] == "Updated"
    _post(admin_client, f"/categories/{category_id}/delete", {})
    assert db_query("SELECT COUNT(*) FROM categories WHERE id=%s", (category_id,))[0] == 0


def test_category_with_budget_cannot_be_deleted(admin_client, db_query):
    response = _post(admin_client, "/categories/3/delete", {})
    assert response.status_code in {302, 303}
    assert db_query("SELECT COUNT(*) FROM categories WHERE id=3")[0] == 1


def test_expense_create_edit_duplicate_delete_flow(admin_client, db_query):
    payload = {
        "type": "expense",
        "from": "expense",
        "concept": "Release flow expense",
        "amount": "42.50",
        "date": "2026-07",
        "category": "Food",
        "payment_method_id": "1",
        "comment": "Created",
    }
    _post(admin_client, "/records/add", payload)
    record_id = db_query("SELECT id FROM records WHERE concept=%s", (payload["concept"],))[0]
    _post(
        admin_client,
        f"/edit/{record_id}",
        {**payload, "concept": "Release flow edited", "amount": "50.25", "comment": "Updated"},
    )
    assert db_query("SELECT amount, comment FROM records WHERE id=%s", (record_id,)) == (50.25, "Updated")
    _post(
        admin_client,
        f"/duplicate/{record_id}",
        {**payload, "concept": "Release flow duplicate"},
    )
    assert db_query("SELECT COUNT(*) FROM records WHERE concept='Release flow duplicate'")[0] == 1
    _post(admin_client, f"/delete/{record_id}", {"from": "expense"})
    assert db_query("SELECT COUNT(*) FROM records WHERE id=%s", (record_id,))[0] == 0


def test_loan_usage_create_update_delete_flow(admin_client, db_query):
    _post(
        admin_client,
        "/loans/1/usages/add",
        {"concept": "Flow usage", "amount": "30", "date": "2026-07", "category": "Food"},
    )
    usage_id = db_query("SELECT id FROM loan_usages WHERE concept='Flow usage'")[0]
    _post(
        admin_client,
        f"/loans/1/usages/{usage_id}/update",
        {"concept": "Flow usage updated", "amount": "35", "date": "2026-07", "category": "Food"},
    )
    assert db_query("SELECT amount FROM loan_usages WHERE id=%s", (usage_id,))[0] == 35
    _post(admin_client, f"/loans/1/usages/{usage_id}/delete", {})
    assert db_query("SELECT COUNT(*) FROM loan_usages WHERE id=%s", (usage_id,))[0] == 0


def test_loans_excluded_from_analytics_are_visually_muted(admin_client, db_query):
    db_query(
        "UPDATE loans SET exclude_from_dashboard=TRUE WHERE id=2",
        fetch="none",
    )

    response = admin_client.get("/loans")

    assert response.status_code == 200
    excluded_row = (
        rb'<tr class="row-link loan-excluded-row" data-href="/loans/2"'
    )
    included_row = rb'<tr class="row-link" data-href="/loans/1"'
    assert excluded_row in response.data
    assert included_row in response.data
    assert (
        b".table-clean tbody tr.loan-excluded-row {\n"
        b"        opacity: 0.68;"
    ) in response.data
    assert b"background-color: #f1f3f5;" in response.data


def test_budget_create_update_and_actual_spending(admin_client, db_query):
    response = admin_client.get("/budgets?month=2026-07")
    assert response.status_code == 200
    assert b"1.334,56" in response.data
    _post(admin_client, "/budgets/2/save", {"month": "2026-07", "amount": "300"})
    assert db_query(
        "SELECT amount FROM category_budgets WHERE category_id=2 AND month='2026-07'"
    )[0] == 300
    _post(admin_client, "/budgets/2/save", {"month": "2026-07", "amount": "350"})
    assert db_query(
        "SELECT amount FROM category_budgets WHERE category_id=2 AND month='2026-07'"
    )[0] == 350


def test_budget_history_is_read_only_and_uses_value_effective_that_month(admin_client, db_query):
    db_query(
        """INSERT INTO category_budgets (category_id, month, amount)
           VALUES (1, '2026-06', 700)
           ON CONFLICT (category_id, month) DO UPDATE SET amount=EXCLUDED.amount""",
        fetch="none",
    )
    response = admin_client.get("/budgets?month=2026-06")
    assert response.status_code == 200
    assert b"700,00" in response.data
    assert b"/budgets/1/save" not in response.data

    _post(admin_client, "/budgets/1/save", {"month": "2026-06", "amount": "1600"})
    values = db_query(
        "SELECT month, amount FROM category_budgets WHERE category_id=1 ORDER BY month",
        fetch="all",
    )
    assert values == [("2026-06", Decimal("700.00")), ("2026-07", Decimal("1600.00"))]


def test_bank_detail_pagination_loads_second_page(admin_client, db_query):
    for index in range(11):
        db_query(
            """
            INSERT INTO records (concept, amount, date, type, payment_method_id, created_by)
            VALUES (%s, 10, '2026-07', 'expense', 1, 'admin_test')
            """,
            (f"Paginated expense {index:02d}",),
            fetch="none",
        )
    response = admin_client.get("/payment-methods/banks/1?page=2")
    assert response.status_code == 200
    assert b"Paginated expense 00" in response.data


def test_bank_relationships_show_cards_with_accounts_and_exclude_loans(admin_client, db_query):
    db_query(
        """INSERT INTO loans (name, bank_name, bank_id, principal_amount, term_months, monthly_payment,
                              start_date, status, loan_type, created_by)
           VALUES ('Only-bank loan', 'Empty Bank', 3, 3000, 12, 250, '2026-01', 'active', 'standard', 'admin_test')""",
        fetch="none",
    )
    response = admin_client.get("/payment-methods/relationships")
    assert response.status_code == 200
    assert b"Only-bank loan" not in response.data
    assert b"Test Card" in response.data
    assert b"Test Account" in response.data
    assert b'class="dependency-links-svg"' in response.data
    assert b'data-account-node="2"' in response.data
    assert b'data-parent-account-node="2"' in response.data
    assert response.data.index(b"Test Bank") < response.data.index(b"Empty Bank")


def test_bank_graphs_and_detail_add_associated_loan_payments_not_usages(admin_client):
    response = admin_client.get("/payment-methods/kpi?scope=banks&year=2026")
    assert response.status_code == 200
    assert b'"labels": ["Empty Bank", "Inactive Bank", "Test Bank"]' in response.data
    assert b'"total_spent": [0.0, 0.0, 1334.56]' in response.data

    detail = admin_client.get("/payment-methods/banks/1")
    assert detail.status_code == 200
    assert b"1.334,56" in detail.data
    assert b"1.409,56" not in detail.data
    assert "Pagos recientes de préstamos".encode() not in detail.data
    assert "Usos recientes de préstamos".encode() not in detail.data


def test_loan_only_bank_has_debt_kpis_without_balance(admin_client, db_query):
    db_query(
        """INSERT INTO loans (name, bank_name, bank_id, principal_amount, term_months, monthly_payment,
                              start_date, status, loan_type, total_repayment_amount, created_by)
           VALUES ('Loan-only debt', 'Empty Bank', 3, 3000, 12, 275, '2026-01', 'active',
                   'interest', 3300, 'admin_test')""",
        fetch="none",
    )
    response = admin_client.get("/payment-methods/banks/3")
    assert response.status_code == 200
    assert "Sin información de saldo: este banco solo tiene préstamos asociados".encode() in response.data
    assert "Capital prestado".encode() in response.data
    assert "Deuda pendiente".encode() in response.data
    assert "Importe amortizado".encode() in response.data
    assert "Cuota mensual".encode() in response.data
    assert b"Loan-only debt" in response.data
    assert b"3.000,00" in response.data
    assert b"3.300,00" in response.data
    assert b"275,00" in response.data
