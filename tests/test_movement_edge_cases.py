import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data):
    return client.post(
        path,
        data={**data, "csrf_token": "test-csrf-token"},
        follow_redirects=False,
    )


def _expense_payload(**overrides):
    payload = {
        "from": "expense",
        "type": "expense",
        "concept": "Deferred edge",
        "amount": "25",
        "date": "2026-07",
        "category": "Food",
        "payment_method_id": "1",
        "is_deferred": "1",
        "deferred_total": "3",
    }
    payload.update(overrides)
    return payload


def test_deferred_series_can_shrink_and_rejects_edit_from_later_installment(
    admin_client, db_query
):
    _post(admin_client, "/records/add", _expense_payload())
    rows = db_query(
        """
        SELECT id, deferred_index, deferred_total
        FROM records WHERE concept='Deferred edge'
        ORDER BY deferred_index
        """,
        fetch="all",
    )
    assert [(row[1], row[2]) for row in rows] == [(1, 3), (2, 3), (3, 3)]

    first_id = rows[0][0]
    response = _post(
        admin_client,
        f"/edit/{first_id}",
        _expense_payload(deferred_total="2", deferred_scope="series"),
    )
    assert response.status_code in {302, 303}
    assert db_query(
        """
        SELECT deferred_index, deferred_total
        FROM records WHERE concept='Deferred edge'
        ORDER BY deferred_index
        """,
        fetch="all",
    ) == [(1, 2), (2, 2)]

    second_id = db_query(
        "SELECT id FROM records WHERE concept='Deferred edge' AND deferred_index=2"
    )[0]
    response = _post(
        admin_client,
        f"/edit/{second_id}",
        _expense_payload(deferred_total="4"),
    )
    assert "Installments%20can%20only%20be%20changed" in response.headers["Location"]


def test_edit_validation_rejects_invalid_account_loan_and_missing_category(
    admin_client,
):
    missing_category = _post(
        admin_client,
        "/edit/1",
        _expense_payload(category="", is_deferred="0"),
    )
    assert "Select%20a%20category" in missing_category.headers["Location"]

    inactive_account = _post(
        admin_client,
        "/edit/1",
        _expense_payload(payment_method_id="3", is_deferred="0"),
    )
    assert "Select%20an%20active%20account%20or%20card" in inactive_account.headers[
        "Location"
    ]

    invalid_loan = _post(
        admin_client,
        "/edit/1",
        _expense_payload(
            is_deferred="0",
            is_loan_payment="1",
            loan_id="9999",
        ),
    )
    assert "Select%20an%20active%20loan" in invalid_loan.headers["Location"]
