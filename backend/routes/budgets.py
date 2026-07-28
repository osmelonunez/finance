from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging
from flask import Blueprint, redirect, render_template, request, session, url_for

from db import get_db
from dashboard_cache import invalidate_dashboard_cache
from feature_flags import budgets_enabled
from validators import parse_year_month


budgets_bp = Blueprint("budgets", __name__)
logger = logging.getLogger("finance.budgets")


@budgets_bp.before_request
def block_disabled_budgets_module():
    if not budgets_enabled():
        return redirect("/")


def _valid_month(raw_value):
    fallback = datetime.now().replace(day=1)
    parsed = parse_year_month(raw_value or "", fallback)
    if parsed > fallback:
        parsed = fallback
    return parsed.strftime("%Y-%m")


def _previous_month(month):
    parsed = datetime.strptime(month, "%Y-%m")
    if parsed.month == 1:
        return f"{parsed.year - 1}-12"
    return f"{parsed.year}-{parsed.month - 1:02d}"


def _next_month(month):
    parsed = datetime.strptime(month, "%Y-%m")
    if parsed.month == 12:
        return f"{parsed.year + 1}-01"
    return f"{parsed.year}-{parsed.month + 1:02d}"


def _parse_budget_amount(raw_value):
    try:
        amount = Decimal((raw_value or "").strip())
    except (InvalidOperation, AttributeError):
        return None
    if amount <= 0 or amount > Decimal("9999999999.99"):
        return None
    return amount


def _budget_state(spent, budget):
    if budget is None:
        return "unbudgeted"
    percentage = (Decimal(spent or 0) / Decimal(budget)) * 100
    if percentage >= 100:
        return "exceeded"
    if percentage >= 90:
        return "danger"
    if percentage >= 80:
        return "warning"
    return "normal"


@budgets_bp.route("/budgets")
def budgets():
    month = _valid_month(request.args.get("month"))
    current_month = datetime.now().strftime("%Y-%m")
    is_current_month = month == current_month
    status_filter = (request.args.get("status") or "all").strip().lower()
    if status_filter not in {"all", "risk", "exceeded", "unbudgeted"}:
        status_filter = "all"

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    b.id,
                    b.amount,
                    b.month,
                    b.is_disabled,
                    COALESCE(SUM(
                        CASE
                            WHEN r.type='expense' THEN r.amount
                            ELSE 0
                        END
                    ), 0) AS spent
                FROM categories c
                LEFT JOIN LATERAL (
                    SELECT cb.id, cb.amount, cb.month, cb.is_disabled
                    FROM category_budgets cb
                    WHERE cb.category_id=c.id AND cb.month <= %s
                    ORDER BY cb.month DESC
                    LIMIT 1
                ) b ON TRUE
                LEFT JOIN records r
                    ON r.category_id=c.id AND r.date=%s
                GROUP BY c.id, c.name, b.id, b.amount, b.month, b.is_disabled
                ORDER BY c.name
                """,
                (month, month),
            )
            rows = cur.fetchall()

    all_categories = []
    for category_id, name, budget_id, amount, budget_month, is_disabled, spent in rows:
        budget = Decimal(amount) if amount is not None and not is_disabled else None
        actual = Decimal(spent or 0)
        percentage = float((actual / budget) * 100) if budget else 0
        state = _budget_state(actual, budget)
        category = {
            "id": category_id,
            "name": name,
            "budget_id": budget_id,
            "budget": budget,
            "budget_month": budget_month,
            "spent": actual,
            "remaining": budget - actual if budget else None,
            "percentage": percentage,
            "bar_percentage": min(percentage, 100),
            "state": state,
        }
        all_categories.append(category)

    categories = [
        item
        for item in all_categories
        if status_filter == "all"
        or (status_filter == "risk" and item["state"] in {"warning", "danger", "exceeded"})
        or (status_filter == "exceeded" and item["state"] == "exceeded")
        or (status_filter == "unbudgeted" and item["state"] == "unbudgeted")
    ]
    budgeted = [item for item in all_categories if item["budget"] is not None]
    total_budget = sum((item["budget"] for item in budgeted), Decimal("0"))
    total_spent = sum((item["spent"] for item in budgeted), Decimal("0"))
    summary = {
        "budget": total_budget,
        "spent": total_spent,
        "remaining": total_budget - total_spent,
        "risk_count": sum(1 for item in budgeted if item["state"] in {"warning", "danger"}),
        "exceeded_count": sum(1 for item in budgeted if item["state"] == "exceeded"),
    }
    return render_template(
        "budgets.html",
        month=month,
        current_month=current_month,
        is_current_month=is_current_month,
        previous_month=_previous_month(month),
        next_month=_next_month(month) if not is_current_month else None,
        categories=categories,
        summary=summary,
        status_filter=status_filter,
        error=request.args.get("error"),
        current_page="budgets",
    )


@budgets_bp.route("/budgets/<int:category_id>/save", methods=["POST"])
def save_budget(category_id):
    month = datetime.now().strftime("%Y-%m")
    amount = _parse_budget_amount(request.form.get("amount"))
    if amount is None:
        return redirect(
            url_for(
                "budgets.budgets",
                month=month,
                error="Budget must be a valid amount greater than 0.",
            )
        )

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM categories WHERE id=%s", (category_id,))
            if not cur.fetchone():
                return redirect(url_for("budgets.budgets", month=month))
            cur.execute(
                """
                INSERT INTO category_budgets (category_id, month, amount, created_by, updated_by)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (category_id, month)
                DO UPDATE SET
                    amount=EXCLUDED.amount,
                    is_disabled=FALSE,
                    updated_by=EXCLUDED.updated_by,
                    updated_at=NOW()
                """,
                (category_id, month, amount, session.get("user_name"), session.get("user_name")),
            )
            conn.commit()
    invalidate_dashboard_cache()
    logger.info(
        "budget_save user=%s category_id=%s month=%s amount=%s",
        session.get("user_name"),
        category_id,
        month,
        amount,
    )
    return redirect(url_for("budgets.budgets", month=month))


@budgets_bp.route("/budgets/<int:category_id>/remove", methods=["POST"])
def remove_budget(category_id):
    month = datetime.now().strftime("%Y-%m")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM categories WHERE id=%s", (category_id,))
            if not cur.fetchone():
                return redirect(url_for("budgets.budgets", month=month))
            cur.execute(
                """
                INSERT INTO category_budgets (
                    category_id, month, amount, is_disabled, created_by, updated_by
                )
                VALUES (%s, %s, NULL, TRUE, %s, %s)
                ON CONFLICT (category_id, month)
                DO UPDATE SET
                    amount=NULL,
                    is_disabled=TRUE,
                    updated_by=EXCLUDED.updated_by,
                    updated_at=NOW()
                """,
                (category_id, month, session.get("user_name"), session.get("user_name")),
            )
            conn.commit()
    invalidate_dashboard_cache()
    logger.info(
        "budget_remove user=%s category_id=%s month=%s",
        session.get("user_name"),
        category_id,
        month,
    )
    return redirect(url_for("budgets.budgets", month=month))
