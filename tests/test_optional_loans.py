import pytest

from feature_flags import clear_feature_flags_cache


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _set_loans_module(admin_client, enabled):
    response = admin_client.post(
        "/management/modules",
        data={"csrf_token": "test-csrf-token", **({"loans_enabled": "1", "budgets_enabled": "1"} if enabled else {"budgets_enabled": "1"})},
        follow_redirects=False,
    )
    assert response.status_code == 302


def _set_budgets_module(admin_client, enabled):
    response = admin_client.post(
        "/management/modules",
        data={"csrf_token": "test-csrf-token", **({"loans_enabled": "1", "budgets_enabled": "1"} if enabled else {"loans_enabled": "1"})},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_disabling_loans_hides_ui_blocks_routes_and_preserves_data(admin_client, db_query):
    loan_count = db_query("SELECT COUNT(*) FROM loans")[0]
    _set_loans_module(admin_client, False)

    dashboard = admin_client.get("/")
    assert b'href="/loans"' not in dashboard.data
    assert admin_client.get("/loans", follow_redirects=False).status_code == 302
    expense_add = admin_client.get("/records/add?from=expense")
    assert b"Loan payment" not in expense_add.data
    reports = admin_client.get("/reports")
    assert b'name="loan_id"' not in reports.data
    bank_detail = admin_client.get("/payment-methods/banks/1")
    assert b"Associated loans" not in bank_detail.data
    movement_detail = admin_client.get("/records/4?from=expense")
    assert b'href="/loans/1"' not in movement_detail.data
    assert admin_client.get("/edit/4?from=expense", follow_redirects=False).status_code == 302
    assert admin_client.get("/duplicate/4?from=expense", follow_redirects=False).status_code == 302
    assert db_query("SELECT COUNT(*) FROM loans")[0] == loan_count
    assert db_query("SELECT COUNT(*) FROM records WHERE is_loan_payment=TRUE")[0] == 1


def test_reenabling_loans_restores_module_without_losing_data(admin_client, db_query):
    _set_loans_module(admin_client, False)
    _set_loans_module(admin_client, True)
    clear_feature_flags_cache()

    dashboard = admin_client.get("/")
    assert b'href="/loans"' in dashboard.data
    assert admin_client.get("/loans", follow_redirects=False).status_code == 200
    assert db_query("SELECT value FROM settings WHERE key='loans_enabled'")[0] == 1


def test_disabling_budgets_hides_ui_blocks_routes_and_preserves_history(admin_client, db_query):
    budget_count = db_query("SELECT COUNT(*) FROM category_budgets")[0]
    _set_budgets_module(admin_client, False)

    dashboard = admin_client.get("/")
    assert b'href="/budgets"' not in dashboard.data
    assert b"Monthly budget" not in dashboard.data
    assert admin_client.get("/budgets", follow_redirects=False).status_code == 302
    assert db_query("SELECT COUNT(*) FROM category_budgets")[0] == budget_count


def test_reenabling_budgets_restores_module_without_losing_history(admin_client, db_query):
    _set_budgets_module(admin_client, False)
    _set_budgets_module(admin_client, True)
    clear_feature_flags_cache()

    dashboard = admin_client.get("/")
    assert b'href="/budgets"' in dashboard.data
    assert admin_client.get("/budgets", follow_redirects=False).status_code == 200
    assert db_query("SELECT value FROM settings WHERE key='budgets_enabled'")[0] == 1
