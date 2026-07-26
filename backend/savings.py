from decimal import Decimal


def savings_account_balances(cur, through_period=None):
    date_clause = "AND r.date <= %s" if through_period else ""
    params = (through_period,) if through_period else ()
    cur.execute(
        f"""
        SELECT
            account.id,
            account.name,
            account.is_active,
            account.initial_balance,
            account.initial_balance
                + COALESCE(SUM(
                    CASE
                        WHEN r.type='saving' AND method.id=account.id THEN r.amount
                        WHEN r.type='expense' THEN -r.amount
                        ELSE 0
                    END
                ), 0) AS balance
        FROM payment_methods account
        LEFT JOIN payment_methods method
            ON method.id=account.id OR method.parent_account_id=account.id
        LEFT JOIN records r
            ON r.payment_method_id=method.id
            {date_clause}
        WHERE account.kind='bank_account'
          AND account.account_type='savings'
        GROUP BY account.id
        ORDER BY account.name
        """,
        params,
    )
    return [
        {
            "id": row[0],
            "name": row[1],
            "is_active": bool(row[2]),
            "initial_balance": Decimal(row[3] or 0),
            "balance": Decimal(row[4] or 0),
        }
        for row in cur.fetchall()
    ]


def savings_accounts_total(accounts):
    return sum((account["balance"] for account in accounts), Decimal("0"))
