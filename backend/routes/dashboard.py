from datetime import datetime
from flask import Blueprint, render_template, request

from db import get_db
from dashboard_cache import get_cached, make_key, set_cached


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    selected_month = request.args.get(
        "month",
        datetime.now().strftime("%Y-%m")
    )
    try:
        years_span = int(request.args.get("years", "5"))
    except ValueError:
        years_span = 5
    years_span = min(max(years_span, 1), 10)
    cache_key = make_key(selected_month, years_span)
    cached = get_cached(cache_key)
    if cached is not None:
        return render_template(
            "dashboard.html",
            month=selected_month,
            monthly_income=cached["monthly_income"],
            monthly_expense=cached["monthly_expense"],
            monthly_saving=cached["monthly_saving"],
            monthly_balance=cached["monthly_balance"],
            saving_total=cached["saving_total"],
            loan_pending_debt=cached.get("loan_pending_debt", 0),
            loan_pending_this_year=cached.get("loan_pending_this_year", 0),
            loan_monthly_payment=cached.get("loan_monthly_payment", 0),
            active_loan_count=cached.get("active_loan_count", 0),
            history=cached["history"],
            years_history=cached["years_history"],
            years_span=years_span,
            current_page="dashboard"
        )

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) AS income,
                    COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END), 0) AS expense,
                    COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END), 0) AS saving
                FROM records
                WHERE date=%s
                """,
                (selected_month,)
            )
            row = cur.fetchone()
            monthly_income = row[0]
            monthly_expense = row[1]
            monthly_saving = row[2]

            monthly_balance = monthly_income - monthly_expense - monthly_saving

            cur.execute(
                """
                SELECT
                    COALESCE((SELECT value FROM settings WHERE key='initial_saving'), 0) AS initial_saving,
                    COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END), 0) AS total_saving,
                    COALESCE(SUM(CASE WHEN type='expense' AND source='saving' THEN amount ELSE 0 END), 0) AS saving_spent
                FROM records
                """
            )
            row = cur.fetchone()
            initial_saving = row[0] if row else 0
            total_saving = row[1] if row else 0
            saving_spent = row[2] if row else 0

            saving_total = initial_saving + total_saving - saving_spent

            cur.execute(
                """
                WITH paid AS (
                    SELECT loan_id, SUM(amount) AS paid_amount
                    FROM records
                    WHERE type='expense' AND is_loan_payment=TRUE
                    GROUP BY loan_id
                )
                SELECT
                    COALESCE(SUM(GREATEST(l.principal_amount - COALESCE(paid.paid_amount, 0), 0)), 0),
                    COALESCE(SUM(COALESCE(l.monthly_payment, 0)), 0),
                    COUNT(l.id)
                FROM loans l
                LEFT JOIN paid ON paid.loan_id = l.id
                WHERE l.status = 'active'
                  AND COALESCE(l.exclude_from_dashboard, FALSE) = FALSE
                """
            )
            row = cur.fetchone()
            loan_pending_debt = row[0] if row else 0
            loan_monthly_payment = row[1] if row else 0
            active_loan_count = row[2] if row else 0

            cur.execute(
                """
                WITH selected_bounds AS (
                    SELECT
                        TO_DATE(%s, 'YYYY-MM') AS start_month,
                        DATE_TRUNC('year', TO_DATE(%s, 'YYYY-MM')) + INTERVAL '11 months' AS end_month
                ),
                paid AS (
                    SELECT loan_id, SUM(amount) AS paid_amount
                    FROM records
                    WHERE type='expense' AND is_loan_payment=TRUE
                    GROUP BY loan_id
                ),
                loan_plan AS (
                    SELECT
                        GREATEST(
                            TO_DATE(l.start_date, 'YYYY-MM'),
                            selected_bounds.start_month
                        ) AS payment_start,
                        LEAST(
                            TO_DATE(l.start_date, 'YYYY-MM') + ((l.term_months - 1) * INTERVAL '1 month'),
                            selected_bounds.end_month
                        ) AS payment_end,
                        COALESCE(l.monthly_payment, 0) AS monthly_payment,
                        GREATEST(l.principal_amount - COALESCE(paid.paid_amount, 0), 0) AS pending_debt
                    FROM loans l
                    CROSS JOIN selected_bounds
                    LEFT JOIN paid ON paid.loan_id = l.id
                    WHERE l.status = 'active'
                      AND COALESCE(l.exclude_from_dashboard, FALSE) = FALSE
                )
                SELECT COALESCE(SUM(LEAST(
                    pending_debt,
                    monthly_payment * GREATEST(
                        (
                            (
                                DATE_PART('year', payment_end)::int
                                - DATE_PART('year', payment_start)::int
                            ) * 12
                            + DATE_PART('month', payment_end)::int
                            - DATE_PART('month', payment_start)::int
                            + 1
                        ),
                        0
                    )
                )), 0)
                FROM loan_plan
                WHERE pending_debt > 0
                  AND monthly_payment > 0
                  AND payment_start <= payment_end
                """,
                (selected_month, selected_month),
            )
            row = cur.fetchone()
            loan_pending_this_year = row[0] if row else 0

            cur.execute(
                """
                WITH months AS (
                    SELECT TO_CHAR(d, 'YYYY-MM') AS month_key
                    FROM GENERATE_SERIES(
                        DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months',
                        DATE_TRUNC('month', CURRENT_DATE),
                        INTERVAL '1 month'
                    ) AS d
                ),
                loan_debt AS (
                    SELECT
                        m.month_key,
                        COALESCE(SUM(GREATEST(
                            l.principal_amount - COALESCE((
                                SELECT SUM(r.amount)
                                FROM records r
                                WHERE r.loan_id = l.id
                                  AND r.type='expense'
                                  AND r.is_loan_payment=TRUE
                                  AND r.date <= m.month_key
                            ), 0),
                            0
                        )), 0) AS pending_debt
                    FROM months m
                    LEFT JOIN loans l
                      ON l.status = 'active'
                     AND COALESCE(l.exclude_from_dashboard, FALSE) = FALSE
                     AND l.start_date <= m.month_key
                    GROUP BY m.month_key
                )
                SELECT
                    m.month_key,
                    COALESCE(SUM(CASE WHEN e.type='income' THEN e.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN e.type='expense' AND e.source='monthly' THEN e.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN e.type='saving' THEN e.amount ELSE 0 END), 0),
                    COALESCE(ld.pending_debt, 0)
                FROM months m
                LEFT JOIN records e ON e.date = m.month_key
                LEFT JOIN loan_debt ld ON ld.month_key = m.month_key
                GROUP BY m.month_key, ld.pending_debt
                ORDER BY m.month_key ASC
                """
            )
            rows = cur.fetchall()

            cur.execute(
                """
                WITH years AS (
                    SELECT GENERATE_SERIES(
                        EXTRACT(YEAR FROM CURRENT_DATE)::int - %s + 1,
                        EXTRACT(YEAR FROM CURRENT_DATE)::int
                    )::int AS year
                ),
                record_totals AS (
                    SELECT substring(date, 1, 4)::int AS year,
                           COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),0) AS income,
                           COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END),0) AS expense,
                           COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END),0) AS saving
                    FROM records
                    WHERE substring(date, 1, 4) ~ '^[0-9]{4}$'
                    GROUP BY year
                ),
                loan_debt AS (
                    SELECT
                        y.year,
                        COALESCE(SUM(GREATEST(
                            l.principal_amount - COALESCE((
                                SELECT SUM(r.amount)
                                FROM records r
                                WHERE r.loan_id = l.id
                                  AND r.type='expense'
                                  AND r.is_loan_payment=TRUE
                                  AND r.date <= y.year::text || '-12'
                            ), 0),
                            0
                        )), 0) AS pending_debt
                    FROM years y
                    LEFT JOIN loans l
                      ON l.status = 'active'
                     AND COALESCE(l.exclude_from_dashboard, FALSE) = FALSE
                     AND substring(l.start_date, 1, 4)::int <= y.year
                    GROUP BY y.year
                )
                SELECT y.year::text,
                       COALESCE(rt.income, 0),
                       COALESCE(rt.expense, 0),
                       COALESCE(rt.saving, 0),
                       COALESCE(ld.pending_debt, 0)
                FROM years y
                LEFT JOIN record_totals rt ON rt.year = y.year
                LEFT JOIN loan_debt ld ON ld.year = y.year
                ORDER BY y.year ASC
                """,
                (years_span,),
            )
            years_rows = cur.fetchall()

    history = rows
    payload = {
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "monthly_saving": monthly_saving,
        "monthly_balance": monthly_balance,
        "saving_total": saving_total,
        "loan_pending_debt": loan_pending_debt,
        "loan_pending_this_year": loan_pending_this_year,
        "loan_monthly_payment": loan_monthly_payment,
        "active_loan_count": active_loan_count,
        "history": history,
        "years_history": years_rows,
    }
    set_cached(cache_key, payload)

    return render_template(
        "dashboard.html",
        month=selected_month,
        monthly_income=payload["monthly_income"],
        monthly_expense=payload["monthly_expense"],
        monthly_saving=payload["monthly_saving"],
        monthly_balance=payload["monthly_balance"],
        saving_total=payload["saving_total"],
        loan_pending_debt=payload["loan_pending_debt"],
        loan_pending_this_year=payload["loan_pending_this_year"],
        loan_monthly_payment=payload["loan_monthly_payment"],
        active_loan_count=payload["active_loan_count"],
        history=payload["history"],
        years_history=payload["years_history"],
        years_span=years_span,
        current_page="dashboard"
    )
