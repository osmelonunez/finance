from datetime import datetime
from flask import Blueprint, render_template, request

from db import get_db


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

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(amount),0) FROM records WHERE type='income' AND date=%s",
                (selected_month,)
            )
            monthly_income = cur.fetchone()[0]

            cur.execute("""
                SELECT COALESCE(SUM(amount),0)
                FROM records
                WHERE type='expense' AND source='monthly' AND date=%s
            """, (selected_month,))
            monthly_expense = cur.fetchone()[0]

            cur.execute(
                "SELECT COALESCE(SUM(amount),0) FROM records WHERE type='saving' AND date=%s",
                (selected_month,)
            )
            monthly_saving = cur.fetchone()[0]

            monthly_balance = monthly_income - monthly_expense - monthly_saving

            cur.execute(
                "SELECT COALESCE(value,0) FROM settings WHERE key='initial_saving'"
            )
            row = cur.fetchone()
            initial_saving = row[0] if row else 0

            cur.execute(
                "SELECT COALESCE(SUM(amount),0) FROM records WHERE type='saving'"
            )
            total_saving = cur.fetchone()[0]

            cur.execute("""
                SELECT COALESCE(SUM(amount),0)
                FROM records
                WHERE type='expense' AND source='saving'
            """)
            saving_spent = cur.fetchone()[0]

            saving_total = initial_saving + total_saving - saving_spent

            cur.execute(
                """
                WITH months AS (
                    SELECT TO_CHAR(d, 'YYYY-MM') AS month_key
                    FROM GENERATE_SERIES(
                        DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months',
                        DATE_TRUNC('month', CURRENT_DATE),
                        INTERVAL '1 month'
                    ) AS d
                )
                SELECT
                    m.month_key,
                    COALESCE(SUM(CASE WHEN e.type='income' THEN e.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN e.type='expense' AND e.source='monthly' THEN e.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN e.type='saving' THEN e.amount ELSE 0 END), 0)
                FROM months m
                LEFT JOIN records e ON e.date = m.month_key
                GROUP BY m.month_key
                ORDER BY m.month_key ASC
                """
            )
            rows = cur.fetchall()

            cur.execute(
                """
                SELECT substring(date, 1, 4) AS year,
                       COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),0),
                       COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END),0),
                       COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END),0)
                FROM records
                WHERE substring(date, 1, 4) ~ '^[0-9]{4}$'
                  AND substring(date, 1, 4)::int >= (EXTRACT(YEAR FROM CURRENT_DATE)::int - %s + 1)
                GROUP BY year
                ORDER BY year ASC
                """,
                (years_span,),
            )
            years_rows = cur.fetchall()

    history = rows

    return render_template(
        "dashboard.html",
        month=selected_month,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_saving=monthly_saving,
        monthly_balance=monthly_balance,
        saving_total=saving_total,
        history=history,
        years_history=years_rows,
        years_span=years_span,
        current_page="dashboard"
    )
