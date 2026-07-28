import pytest

from dashboard_cache import invalidate_dashboard_cache


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data):
    return client.post(
        path,
        data={**data, "csrf_token": "test-csrf-token"},
        follow_redirects=False,
    )


def test_savings_account_can_be_created_with_initial_balance(admin_client, db_query):
    response = _post(
        admin_client,
        "/payment-methods/add",
        {
            "name": "Second Savings",
            "kind": "bank_account",
            "bank_id": "1",
            "account_ref": "SAV-002",
            "account_type": "savings",
            "initial_balance": "250.50",
            "is_active": "1",
        },
    )

    assert response.status_code in {302, 303}
    assert db_query(
        """
        SELECT account_type, initial_balance
        FROM payment_methods
        WHERE name='Second Savings'
        """
    ) == ("savings", 250.5)


def test_dashboard_only_shows_savings_breakdown_for_multiple_accounts(
    admin_client, db_query
):
    one_account = admin_client.get("/?month=2026-07")
    assert one_account.status_code == 200
    assert b"Test Savings:" not in one_account.data

    db_query(
        """
        INSERT INTO payment_methods (
            name, kind, bank_name, is_active, bank_id, account_type, initial_balance
        )
        VALUES ('Second Savings', 'bank_account', 'Test Bank', TRUE, 1, 'savings', 250)
        """,
        fetch="none",
    )
    invalidate_dashboard_cache()

    two_accounts = admin_client.get("/?month=2026-07")
    assert b"Test Savings:" in two_accounts.data
    assert b"Second Savings:" in two_accounts.data


def test_saving_requires_an_active_savings_account(admin_client, db_query):
    form = admin_client.get("/records/add?from=saving")
    assert form.status_code == 200
    assert b'name="source"' not in form.data
    assert "[Test Bank · Cuenta de ahorro] Test Savings".encode() in form.data
    assert b"Test Account" not in form.data

    rejected = _post(
        admin_client,
        "/records/add?from=saving",
        {
            "from": "saving",
            "type": "saving",
            "concept": "Missing destination",
            "amount": "100",
            "date": "2026-07",
        },
    )
    assert rejected.status_code == 200
    assert b"Select an active savings account." in rejected.data

    created = _post(
        admin_client,
        "/records/add?from=saving",
        {
            "from": "saving",
            "type": "saving",
            "concept": "Savings contribution",
            "amount": "100",
            "date": "2026-07",
            "payment_method_id": "6",
        },
    )
    assert created.status_code in {302, 303}
    assert db_query(
        """
        SELECT type, payment_method_id
        FROM records
        WHERE concept='Savings contribution'
        """
    ) == ("saving", 6)


def test_expense_form_has_typed_accounts_and_requires_category(
    admin_client, db_query
):
    form = admin_client.get("/records/add?from=expense")

    assert form.status_code == 200
    assert b'name="source"' not in form.data
    assert "[Test Bank · Cuenta corriente] Test Account".encode() in form.data
    assert "[Test Bank · Tarjeta] Test Card".encode() in form.data
    assert "[Test Bank · Cuenta de ahorro] Test Savings".encode() in form.data
    assert b'name="category" required' in form.data

    rejected = _post(
        admin_client,
        "/records/add?from=expense",
        {
            "from": "expense",
            "type": "expense",
            "concept": "Expense without category",
            "amount": "25",
            "date": "2026-07",
            "payment_method_id": "2",
        },
    )

    assert rejected.status_code == 200
    assert "Selecciona una categoría.".encode() in rejected.data
    assert db_query(
        "SELECT COUNT(*) FROM records WHERE concept='Expense without category'"
    ) == (0,)


def test_edit_and_duplicate_expenses_reject_missing_category(
    admin_client, db_query
):
    edited = _post(
        admin_client,
        "/edit/1?from=expense",
        {
            "from": "expense",
            "type": "expense",
            "concept": "Edited without category",
            "amount": "1234.56",
            "date": "2026-07",
            "payment_method_id": "1",
        },
    )
    duplicated = _post(
        admin_client,
        "/duplicate/1?from=expense",
        {
            "from": "expense",
            "type": "expense",
            "concept": "Duplicated without category",
            "amount": "1234.56",
            "date": "2026-07",
            "payment_method_id": "1",
        },
    )

    assert edited.status_code in {302, 303}
    assert "Select%20a%20category" in edited.headers["Location"]
    assert duplicated.status_code in {302, 303}
    assert "Select%20a%20category" in duplicated.headers["Location"]
    assert db_query("SELECT concept FROM records WHERE id=1") == ("Test expense",)
    assert db_query(
        "SELECT COUNT(*) FROM records WHERE concept='Duplicated without category'"
    ) == (0,)


def test_edit_and_duplicate_preserve_savings_destination(admin_client, db_query):
    edited = _post(
        admin_client,
        "/edit/3?from=saving",
        {
            "from": "saving",
            "type": "saving",
            "concept": "Edited saving",
            "amount": "550",
            "date": "2026-07",
            "payment_method_id": "6",
        },
    )
    assert edited.status_code in {302, 303}
    assert db_query(
        "SELECT amount, payment_method_id FROM records WHERE id=3"
    ) == (550, 6)

    duplicated = _post(
        admin_client,
        "/duplicate/3?from=saving",
        {
            "from": "saving",
            "type": "saving",
            "concept": "Duplicated saving",
            "amount": "25",
            "date": "2026-07",
            "payment_method_id": "6",
        },
    )
    assert duplicated.status_code in {302, 303}
    assert db_query(
        """
        SELECT type, payment_method_id
        FROM records
        WHERE concept='Duplicated saving'
        """
    ) == ("saving", 6)


def test_expense_from_savings_counts_as_expense_and_reduces_savings(
    admin_client, db_query
):
    created = _post(
        admin_client,
        "/records/add?from=expense",
        {
            "from": "expense",
            "type": "expense",
            "concept": "Savings-funded expense",
            "amount": "200",
            "date": "2026-07",
            "category": "Food",
            "payment_method_id": "6",
        },
    )
    assert created.status_code in {302, 303}
    assert db_query(
        """
        SELECT payment_method_id
        FROM records
        WHERE concept='Savings-funded expense'
        """
    ) == (6,)

    dashboard = admin_client.get("/?month=2026-07")
    assert b"1.534,56" in dashboard.data
    assert b"1.300,00" in dashboard.data

    budgets = admin_client.get("/budgets?month=2026-07")
    assert b"1.534,56" in budgets.data


def test_card_linked_to_savings_reduces_parent_account_balance(
    admin_client, db_query
):
    _post(
        admin_client,
        "/payment-methods/add",
        {
            "name": "Savings Card",
            "kind": "card",
            "parent_account_id": "6",
            "account_ref": "CARD-SAV",
            "is_active": "1",
        },
    )
    card_id = db_query(
        "SELECT id FROM payment_methods WHERE name='Savings Card'"
    )[0]
    _post(
        admin_client,
        "/records/add?from=expense",
        {
            "from": "expense",
            "type": "expense",
            "concept": "Savings card expense",
            "amount": "75",
            "date": "2026-07",
            "category": "Food",
            "payment_method_id": str(card_id),
        },
    )

    dashboard = admin_client.get("/?month=2026-07")
    assert b"1.425,00" in dashboard.data


def test_inactive_savings_account_stays_in_totals_but_not_new_forms(
    admin_client, db_query
):
    db_query(
        "UPDATE payment_methods SET is_active=FALSE WHERE id=6",
        fetch="none",
    )

    dashboard = admin_client.get("/?month=2026-07")
    saving_form = admin_client.get("/records/add?from=saving")
    reports = admin_client.get("/reports?section=summary&type=monthly&period=2026-07")

    assert b"1.500,00" in dashboard.data
    assert b"Test Savings" not in saving_form.data
    assert b"Test Savings" in reports.data
    assert b"Inactive" in reports.data


def test_dashboard_separates_financial_result_from_balance_after_savings(
    admin_client,
):
    dashboard = admin_client.get("/?month=2026-07")

    assert dashboard.status_code == 200
    assert "Ingresos - Gastos".encode() in dashboard.data
    assert b"1.165,44" in dashboard.data
    assert b"665,44" in dashboard.data
    assert dashboard.data.count(b'class="kpi-help"') == 6
    assert "Balance después del ahorro".encode() in dashboard.data
    assert (
        dashboard.data.index(b"<h6>Gasto</h6>")
        < dashboard.data.index("<h6>Ingresos - Gastos</h6>".encode())
        < dashboard.data.index("<h6>Ahorro del mes</h6>".encode())
    )


def test_account_with_initial_balance_cannot_be_deleted(admin_client, db_query):
    _post(
        admin_client,
        "/payment-methods/add",
        {
            "name": "Opening Balance Only",
            "kind": "bank_account",
            "bank_id": "1",
            "account_type": "savings",
            "initial_balance": "10",
            "is_active": "1",
        },
    )
    account_id = db_query(
        "SELECT id FROM payment_methods WHERE name='Opening Balance Only'"
    )[0]

    deleted = _post(admin_client, f"/payment-methods/{account_id}/delete", {})

    assert deleted.status_code in {302, 303}
    assert db_query(
        "SELECT COUNT(*) FROM payment_methods WHERE id=%s", (account_id,)
    ) == (1,)
