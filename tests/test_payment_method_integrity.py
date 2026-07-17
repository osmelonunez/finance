import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data):
    return client.post(path, data={**data, "csrf_token": "test-csrf-token"}, follow_redirects=False)


def test_account_or_card_requires_a_bank(admin_client, db_query):
    response = _post(
        admin_client,
        "/payment-methods/add",
        {"name": "Orphan Card", "kind": "card", "is_active": "1"},
    )
    assert response.status_code == 302
    assert db_query("SELECT COUNT(*) FROM payment_methods WHERE name='Orphan Card'")[0] == 0


def test_account_or_card_requires_an_active_bank(admin_client, db_query):
    _post(
        admin_client,
        "/payment-methods/add",
        {"name": "Inactive Bank Card", "kind": "card", "bank_id": "2", "is_active": "1"},
    )
    assert db_query("SELECT COUNT(*) FROM payment_methods WHERE name='Inactive Bank Card'")[0] == 0


def test_valid_card_is_created(admin_client, db_query):
    response = _post(
        admin_client,
        "/payment-methods/add",
        {
            "name": "New Test Card",
            "kind": "card",
            "bank_id": "1",
            "account_ref": "NEW-001",
            "is_active": "1",
        },
    )
    assert response.status_code == 302
    assert db_query(
        "SELECT kind, bank_id, is_active FROM payment_methods WHERE name='New Test Card'"
    ) == ("card", 1, True)


def test_payment_method_with_movements_cannot_be_deleted(admin_client, db_query):
    _post(admin_client, "/payment-methods/1/delete", {})
    assert db_query("SELECT COUNT(*) FROM payment_methods WHERE id=1")[0] == 1


def test_unused_payment_method_can_be_deleted(admin_client, db_query):
    _post(admin_client, "/payment-methods/4/delete", {})
    assert db_query("SELECT COUNT(*) FROM payment_methods WHERE id=4")[0] == 0


def test_deactivating_bank_deactivates_linked_methods(admin_client, db_query):
    _post(admin_client, "/payment-methods/banks/1/update", {"name": "Test Bank", "is_active": "0"})
    assert db_query("SELECT is_active FROM banks WHERE id=1")[0] is False
    assert db_query("SELECT COUNT(*) FROM payment_methods WHERE bank_id=1 AND is_active=TRUE")[0] == 0


def test_bank_with_linked_methods_cannot_be_deleted(admin_client, db_query):
    _post(admin_client, "/payment-methods/banks/1/delete", {})
    assert db_query("SELECT COUNT(*) FROM banks WHERE id=1")[0] == 1


def test_inactive_method_cannot_be_assigned_to_new_expense(admin_client, db_query):
    response = _post(
        admin_client,
        "/records/add",
        {
            "type": "expense",
            "from": "expense",
            "concept": "Invalid inactive method",
            "amount": "20",
            "date": "2026-07",
            "source": "monthly",
            "payment_method_id": "3",
        },
    )
    assert response.status_code == 200
    assert db_query("SELECT COUNT(*) FROM records WHERE concept='Invalid inactive method'")[0] == 0
