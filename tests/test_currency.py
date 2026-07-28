import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def test_global_currency_selector_updates_all_money_formatting(admin_client, db_query):
    page = admin_client.get("/management/system")
    assert page.status_code == 200
    assert b'name="currency"' in page.data
    assert b'EUR' in page.data
    assert page.data.count(b'<option value=') >= 15

    response = admin_client.post(
        "/management/currency",
        data={"currency": "USD", "csrf_token": "test-csrf-token"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert db_query("SELECT text_value FROM settings WHERE key='currency'")[0] == "USD"

    dashboard = admin_client.get("/")
    assert b"$" in dashboard.data


def test_invalid_global_currency_falls_back_to_eur(admin_client, db_query):
    admin_client.post(
        "/management/currency",
        data={"currency": "invalid", "csrf_token": "test-csrf-token"},
        follow_redirects=False,
    )
    assert db_query("SELECT text_value FROM settings WHERE key='currency'")[0] == "EUR"
