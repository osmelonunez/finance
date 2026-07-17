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


def test_expense_create_edit_duplicate_delete_flow(admin_client, db_query):
    payload = {
        "type": "expense",
        "from": "expense",
        "concept": "Release flow expense",
        "amount": "42.50",
        "date": "2026-07",
        "source": "monthly",
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


def test_bank_detail_pagination_loads_second_page(admin_client, db_query):
    for index in range(11):
        db_query(
            """
            INSERT INTO records (concept, amount, date, type, source, payment_method_id, created_by)
            VALUES (%s, 10, '2026-07', 'expense', 'monthly', 1, 'admin_test')
            """,
            (f"Paginated expense {index:02d}",),
            fetch="none",
        )
    response = admin_client.get("/payment-methods/banks/1?page=2")
    assert response.status_code == 200
    assert b"Paginated expense 00" in response.data
