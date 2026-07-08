from decimal import Decimal, InvalidOperation
import logging
from urllib.parse import quote

from flask import Blueprint, redirect, render_template, request, session

from dashboard_cache import invalidate_dashboard_cache
from db import get_db
from validators import parse_year_month, validate_concept


loans_bp = Blueprint("loans", __name__)
logger = logging.getLogger("finance.loans")
LOAN_DETAIL_PAGE_SIZE = 8


def _parse_positive_decimal(value, field_name):
    try:
        amount = Decimal((value or "").strip())
    except (InvalidOperation, AttributeError):
        return None, f"{field_name} must be a valid number."
    if amount <= 0:
        return None, f"{field_name} must be greater than 0."
    return amount, None


def _parse_non_negative_decimal(value, field_name):
    try:
        amount = Decimal((value or "").strip())
    except (InvalidOperation, AttributeError):
        return None, f"{field_name} must be a valid number."
    if amount < 0:
        return None, f"{field_name} must be greater than or equal to 0."
    return amount, None


def _parse_positive_int(value, field_name):
    try:
        parsed = int((value or "").strip())
    except (TypeError, ValueError):
        return None, f"{field_name} must be a valid number."
    if parsed <= 0:
        return None, f"{field_name} must be greater than 0."
    return parsed, None


def _month_index(year_month):
    return year_month.year * 12 + year_month.month


def _recalculate_term_for_start_change(old_start_value, old_term_months, new_start):
    old_start = parse_year_month(old_start_value, None)
    if not old_start or not old_term_months:
        return None
    original_end_index = _month_index(old_start) + int(old_term_months) - 1
    recalculated = original_end_index - _month_index(new_start) + 1
    return recalculated if recalculated > 0 else None


def _loan_query(where="1=1"):
    return f"""
        SELECT
            l.id,
            l.name,
            COALESCE(b.name, l.bank_name) AS bank_name,
            l.principal_amount,
            l.term_months,
            l.monthly_payment,
            l.start_date,
            l.description,
            l.status,
            COALESCE(SUM(CASE WHEN r.is_loan_payment THEN r.amount ELSE 0 END), 0) AS paid_amount,
            CASE
                WHEN l.status = 'paid' THEN l.term_months
                ELSE LEAST(
                    l.term_months,
                    GREATEST(
                        (
                            (
                                DATE_PART('year', DATE_TRUNC('month', CURRENT_DATE))::int
                                - DATE_PART('year', TO_DATE(l.start_date, 'YYYY-MM'))::int
                            ) * 12
                            + DATE_PART('month', DATE_TRUNC('month', CURRENT_DATE))::int
                            - DATE_PART('month', TO_DATE(l.start_date, 'YYYY-MM'))::int
                            + 1
                        ),
                        0
                    )
                )
            END AS payments_count,
            l.exclude_from_dashboard,
            l.is_mortgage,
            l.annual_interest_rate,
            l.monthly_principal_amount,
            l.monthly_interest_amount,
            l.loan_type,
            l.total_repayment_amount,
            l.bank_id
        FROM loans l
        LEFT JOIN banks b ON l.bank_id = b.id
        LEFT JOIN records r ON r.loan_id = l.id AND r.type = 'expense'
        WHERE {where}
        GROUP BY l.id, b.name
    """


@loans_bp.route("/loans")
def loans_list():
    status = (request.args.get("status") or "").strip()
    where = "1=1"
    params = []
    if status in {"active", "paid", "cancelled"}:
        where = "l.status=%s"
        params.append(status)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                _loan_query(where) + " ORDER BY l.status, l.start_date DESC, l.id DESC",
                params,
            )
            loans = cur.fetchall()
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(l.principal_amount), 0),
                    COALESCE(SUM(COALESCE(l.total_repayment_amount, l.principal_amount)), 0),
                    COALESCE(SUM(paid.paid_amount), 0),
                    COUNT(CASE WHEN l.status = 'active' THEN 1 END)
                FROM loans l
                LEFT JOIN (
                    SELECT loan_id, SUM(amount) AS paid_amount
                    FROM records
                    WHERE type='expense' AND is_loan_payment=TRUE
                    GROUP BY loan_id
                ) paid ON paid.loan_id = l.id
                WHERE l.status <> 'cancelled'
                  AND COALESCE(l.exclude_from_dashboard, FALSE) = FALSE
                """
            )
            totals = cur.fetchone()

    total_principal = totals[0] if totals else 0
    total_repayment = totals[1] if totals else 0
    total_paid = totals[2] if totals else 0
    active_count = totals[3] if totals else 0
    total_pending = total_repayment - total_paid

    return render_template(
        "loans.html",
        loans=loans,
        f_status=status,
        total_principal=total_principal,
        total_repayment=total_repayment,
        total_paid=total_paid,
        total_pending=total_pending,
        active_count=active_count,
        current_page="loans",
    )


@loans_bp.route("/loans/add", methods=["GET", "POST"])
def loan_add():
    if request.method == "POST":
        name, name_error = validate_concept(request.form.get("name"))
        if name_error:
            return _render_loan_add(name_error, request.form)

        bank_id = _parse_int_or_none(request.form.get("bank_id"))
        if bank_id is None:
            return _render_loan_add("Select a bank.", request.form)

        principal_amount, principal_error = _parse_positive_decimal(
            request.form.get("principal_amount"),
            "Loan amount",
        )
        if principal_error:
            return _render_loan_add(principal_error, request.form)

        term_months, term_error = _parse_positive_int(
            request.form.get("term_months"),
            "Term months",
        )
        if term_error:
            return _render_loan_add(term_error, request.form)

        monthly_payment = None
        raw_monthly_payment = (request.form.get("monthly_payment") or "").strip()
        if raw_monthly_payment:
            monthly_payment, monthly_error = _parse_positive_decimal(
                raw_monthly_payment,
                "Monthly payment",
            )
            if monthly_error:
                return _render_loan_add(monthly_error, request.form)

        loan_type = (request.form.get("loan_type") or "standard").strip()
        if loan_type not in {"standard", "interest", "mortgage"}:
            loan_type = "standard"
        is_mortgage = loan_type == "mortgage"
        is_interest_bearing = loan_type in {"interest", "mortgage"}
        annual_interest_rate = (request.form.get("annual_interest_rate") or "").strip() or None
        if not is_mortgage:
            annual_interest_rate = None

        total_repayment_amount = None
        raw_total_repayment = (request.form.get("total_repayment_amount") or "").strip()
        if raw_total_repayment:
            total_repayment_amount, total_repayment_error = _parse_positive_decimal(
                raw_total_repayment,
                "Total to repay",
            )
            if total_repayment_error:
                return _render_loan_add(total_repayment_error, request.form)
            if total_repayment_amount < principal_amount:
                return _render_loan_add("Total to repay must be greater than or equal to loan amount.", request.form)

        monthly_principal_amount = None
        monthly_interest_amount = None
        if is_mortgage:
            if not monthly_payment:
                return _render_loan_add("Monthly payment is required for mortgages.", request.form)
            monthly_principal_amount, monthly_principal_error = _parse_positive_decimal(
                request.form.get("monthly_principal_amount"),
                "Monthly principal",
            )
            if monthly_principal_error:
                return _render_loan_add(monthly_principal_error, request.form)
            monthly_interest_amount, monthly_interest_error = _parse_non_negative_decimal(
                request.form.get("monthly_interest_amount"),
                "Monthly interest",
            )
            if monthly_interest_error:
                return _render_loan_add(monthly_interest_error, request.form)
            if monthly_principal_amount + monthly_interest_amount != monthly_payment:
                return _render_loan_add("Mortgage principal and interest must match monthly payment.", request.form)

        start_date = (request.form.get("start_date") or "").strip()
        start_date = parse_year_month(start_date, None)
        if not start_date:
            return _render_loan_add("Start date is required.", request.form)
        start_date_value = start_date.strftime("%Y-%m")
        description = (request.form.get("description") or "").strip() or None
        exclude_from_dashboard = request.form.get("exclude_from_dashboard") == "on"

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM banks WHERE id=%s AND is_active=TRUE", (bank_id,))
                bank_row = cur.fetchone()
                if not bank_row:
                    return _render_loan_add("Select a bank.", request.form)
                bank_name = bank_row[0]
                cur.execute(
                    """
                    INSERT INTO loans (
                        name, bank_id, bank_name, principal_amount, term_months, monthly_payment,
                        start_date, description, exclude_from_dashboard, is_mortgage, annual_interest_rate,
                        monthly_principal_amount, monthly_interest_amount, loan_type, total_repayment_amount,
                        created_by, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                    """,
                    (
                        name,
                        bank_id,
                        bank_name,
                        principal_amount,
                        term_months,
                        monthly_payment,
                        start_date_value,
                        description,
                        exclude_from_dashboard,
                        is_mortgage,
                        annual_interest_rate,
                        monthly_principal_amount,
                        monthly_interest_amount,
                        loan_type,
                        total_repayment_amount,
                        session.get("user_name"),
                    ),
                )
                loan_id = cur.fetchone()[0]
                conn.commit()
                invalidate_dashboard_cache()
                logger.info("loan_create user=%s id=%s name=%s", session.get("user_name"), loan_id, name)

        return redirect(f"/loans/{loan_id}")

    return _render_loan_add()


def _render_loan_add(error=None, form_data=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name
                FROM banks
                WHERE is_active=TRUE
                ORDER BY name
                """
            )
            banks = cur.fetchall()
    return render_template(
        "loan_add.html",
        error=error,
        form_data=form_data or {},
        banks=banks,
        current_page="loans",
    )


def _parse_int_or_none(raw_value):
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return None


def _parse_page(raw_value):
    try:
        page = int(raw_value or "1")
    except (TypeError, ValueError):
        return 1
    return max(page, 1)


def _page_count(total_rows):
    return max((total_rows + LOAN_DETAIL_PAGE_SIZE - 1) // LOAN_DETAIL_PAGE_SIZE, 1)


@loans_bp.route("/loans/<int:id>")
def loan_detail(id):
    active_tab = request.args.get("tab")
    if active_tab not in {"usages", "payments"}:
        active_tab = "usages"
    usage_page = _parse_page(request.args.get("usage_page"))
    payment_page = _parse_page(request.args.get("payment_page"))

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(_loan_query("l.id=%s"), (id,))
            loan = cur.fetchone()
            if not loan:
                return redirect("/loans")
            cur.execute("SELECT COUNT(*) FROM loan_usages WHERE loan_id=%s", (id,))
            usage_total_rows = cur.fetchone()[0]
            usage_pages = _page_count(usage_total_rows)
            usage_page = min(usage_page, usage_pages)
            cur.execute(
                """
                SELECT
                    u.id,
                    u.concept,
                    u.amount,
                    u.date,
                    c.name AS category_name,
                    u.comment
                FROM loan_usages u
                LEFT JOIN categories c ON u.category_id = c.id
                WHERE u.loan_id=%s
                ORDER BY u.date DESC, u.id DESC
                LIMIT %s OFFSET %s
                """,
                (id, LOAN_DETAIL_PAGE_SIZE, (usage_page - 1) * LOAN_DETAIL_PAGE_SIZE),
            )
            usages = cur.fetchall()
            cur.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM loan_usages
                WHERE loan_id=%s
                """,
                (id,),
            )
            usage_total = cur.fetchone()[0]
            cur.execute(
                """
                SELECT COUNT(*)
                FROM records
                WHERE loan_id=%s AND type='expense' AND is_loan_payment=TRUE
                """,
                (id,),
            )
            payment_total_rows = cur.fetchone()[0]
            payment_pages = _page_count(payment_total_rows)
            payment_page = min(payment_page, payment_pages)
            cur.execute(
                """
                SELECT id, concept, amount, date, source, comment, loan_principal_amount, loan_interest_amount
                FROM records
                WHERE loan_id=%s AND type='expense' AND is_loan_payment=TRUE
                ORDER BY date DESC, id DESC
                LIMIT %s OFFSET %s
                """,
                (id, LOAN_DETAIL_PAGE_SIZE, (payment_page - 1) * LOAN_DETAIL_PAGE_SIZE),
            )
            payments = cur.fetchall()
            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute(
                """
                SELECT id, name
                FROM banks
                WHERE is_active=TRUE
                ORDER BY name
                """
            )
            banks = cur.fetchall()

    return render_template(
        "loan_detail.html",
        loan=loan,
        usages=usages,
        usage_total=usage_total,
        usage_total_rows=usage_total_rows,
        usage_page=usage_page,
        usage_pages=usage_pages,
        categories=categories,
        payments=payments,
        payment_total_rows=payment_total_rows,
        payment_page=payment_page,
        payment_pages=payment_pages,
        active_tab=active_tab,
        banks=banks,
        current_page="loans",
    )


@loans_bp.route("/loans/<int:id>/usages/add", methods=["POST"])
def loan_usage_add(id):
    concept, concept_error = validate_concept(request.form.get("concept"))
    if concept_error:
        return redirect(f"/loans/{id}?tab=usages&error={quote(concept_error)}")

    amount, amount_error = _parse_positive_decimal(request.form.get("amount"), "Amount")
    if amount_error:
        return redirect(f"/loans/{id}?tab=usages&error={quote(amount_error)}")

    date = (request.form.get("date") or "").strip()
    date = parse_year_month(date, None)
    if not date:
        return redirect(f"/loans/{id}?tab=usages&error={quote('Date is required.')}")
    date_value = date.strftime("%Y-%m")
    category_name = (request.form.get("category") or "").strip()
    comment = (request.form.get("comment") or "").strip() or None

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM loans WHERE id=%s", (id,))
            if not cur.fetchone():
                return redirect("/loans")
            category_id = None
            if category_name:
                cur.execute("SELECT id FROM categories WHERE name=%s", (category_name,))
                category_row = cur.fetchone()
                category_id = category_row[0] if category_row else None
            cur.execute(
                """
                INSERT INTO loan_usages (
                    loan_id, concept, amount, date, category_id, comment,
                    created_by, created_at, updated_at, updated_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                """,
                (
                    id,
                    concept,
                    amount,
                    date_value,
                    category_id,
                    comment,
                    session.get("user_name"),
                    session.get("user_name"),
                ),
            )
            conn.commit()
            logger.info("loan_usage_create user=%s loan_id=%s concept=%s", session.get("user_name"), id, concept)
    return redirect(f"/loans/{id}?tab=usages")


@loans_bp.route("/loans/<int:id>/usages/<int:usage_id>/delete", methods=["POST"])
def loan_usage_delete(id, usage_id):
    usage_page = _parse_page(request.args.get("usage_page"))
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM loan_usages WHERE id=%s AND loan_id=%s", (usage_id, id))
            deleted = cur.rowcount
            conn.commit()
            logger.info(
                "loan_usage_delete user=%s loan_id=%s usage_id=%s deleted=%s",
                session.get("user_name"),
                id,
                usage_id,
                deleted,
            )
    return redirect(f"/loans/{id}?tab=usages&usage_page={usage_page}")


@loans_bp.route("/loans/<int:id>/status", methods=["POST"])
def loan_status(id):
    status = (request.form.get("status") or "").strip()
    if status not in {"active", "paid", "cancelled"}:
        return redirect(f"/loans/{id}?error={quote('Invalid status.')}")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE loans
                SET status=%s, updated_at=NOW(), updated_by=%s
                WHERE id=%s
                """,
                (status, session.get("user_name"), id),
            )
            conn.commit()
            invalidate_dashboard_cache()
            logger.info("loan_status_update user=%s id=%s status=%s", session.get("user_name"), id, status)
    return redirect(f"/loans/{id}")


@loans_bp.route("/loans/<int:id>/details", methods=["POST"])
def loan_details_update(id):
    name, name_error = validate_concept(request.form.get("name"))
    if name_error:
        return redirect(f"/loans/{id}?edit=1&error={quote(name_error)}")

    bank_id = _parse_int_or_none(request.form.get("bank_id"))
    if bank_id is None:
        return redirect(f"/loans/{id}?edit=1&error={quote('Select a bank.')}")

    principal_amount, principal_error = _parse_positive_decimal(
        request.form.get("principal_amount"),
        "Loan amount",
    )
    if principal_error:
        return redirect(f"/loans/{id}?edit=1&error={quote(principal_error)}")

    term_months, term_error = _parse_positive_int(
        request.form.get("term_months"),
        "Term months",
    )
    if term_error:
        return redirect(f"/loans/{id}?edit=1&error={quote(term_error)}")

    start_date = (request.form.get("start_date") or "").strip()
    start_date = parse_year_month(start_date, None)
    if not start_date:
        return redirect(f"/loans/{id}?edit=1&error={quote('Start date is required.')}")
    start_date_value = start_date.strftime("%Y-%m")
    description = (request.form.get("description") or "").strip() or None

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT start_date, term_months FROM loans WHERE id=%s", (id,))
            current_loan = cur.fetchone()
            if not current_loan:
                return redirect("/loans")
    old_start_value, old_term_months = current_loan
    if start_date_value != old_start_value and term_months == old_term_months:
        recalculated_term_months = _recalculate_term_for_start_change(
            old_start_value,
            old_term_months,
            start_date,
        )
        if recalculated_term_months is None:
            return redirect(f"/loans/{id}?edit=1&error={quote('Start date must be before the loan end date.')}")
        term_months = recalculated_term_months

    status = (request.form.get("status") or "").strip()
    if status not in {"active", "paid", "cancelled"}:
        return redirect(f"/loans/{id}?edit=1&error={quote('Invalid status.')}")

    loan_type = (request.form.get("loan_type") or "standard").strip()
    if loan_type not in {"standard", "interest", "mortgage"}:
        loan_type = "standard"
    is_mortgage = loan_type == "mortgage"
    is_interest_bearing = loan_type in {"interest", "mortgage"}
    exclude_from_dashboard = request.form.get("exclude_from_dashboard") == "on"

    annual_interest_rate = (request.form.get("annual_interest_rate") or "").strip() or None
    if not is_mortgage:
        annual_interest_rate = None

    monthly_payment = None
    raw_monthly_payment = (request.form.get("monthly_payment") or "").strip()
    if raw_monthly_payment:
        monthly_payment, monthly_error = _parse_positive_decimal(
            raw_monthly_payment,
            "Monthly payment",
        )
        if monthly_error:
            return redirect(f"/loans/{id}?edit=1&error={quote(monthly_error)}")

    total_repayment_amount = None
    raw_total_repayment = (request.form.get("total_repayment_amount") or "").strip()
    if raw_total_repayment:
        total_repayment_amount, total_repayment_error = _parse_positive_decimal(
            raw_total_repayment,
            "Total to repay",
        )
        if total_repayment_error:
            return redirect(f"/loans/{id}?edit=1&error={quote(total_repayment_error)}")

    if total_repayment_amount is not None and total_repayment_amount < principal_amount:
        return redirect(
            f"/loans/{id}?edit=1&error={quote('Total to repay must be greater than or equal to loan amount.')}"
        )

    monthly_principal_amount = None
    monthly_interest_amount = None
    if is_mortgage:
        if not monthly_payment:
            return redirect(f"/loans/{id}?edit=1&error={quote('Monthly payment is required for mortgages.')}")
        monthly_principal_amount, monthly_principal_error = _parse_positive_decimal(
            request.form.get("monthly_principal_amount"),
            "Monthly principal",
        )
        if monthly_principal_error:
            return redirect(f"/loans/{id}?edit=1&error={quote(monthly_principal_error)}")
        monthly_interest_amount, monthly_interest_error = _parse_non_negative_decimal(
            request.form.get("monthly_interest_amount"),
            "Monthly interest",
        )
        if monthly_interest_error:
            return redirect(f"/loans/{id}?edit=1&error={quote(monthly_interest_error)}")
        if monthly_principal_amount + monthly_interest_amount != monthly_payment:
            return redirect(
                f"/loans/{id}?edit=1&error={quote('Mortgage principal and interest must match monthly payment.')}"
            )

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM banks WHERE id=%s AND is_active=TRUE", (bank_id,))
            bank_row = cur.fetchone()
            if not bank_row:
                return redirect(f"/loans/{id}?edit=1&error={quote('Select a bank.')}")
            bank_name = bank_row[0]
            cur.execute(
                """
                UPDATE loans
                SET name=%s,
                    bank_id=%s,
                    bank_name=%s,
                    principal_amount=%s,
                    term_months=%s,
                    start_date=%s,
                    description=%s,
                    status=%s,
                    exclude_from_dashboard=%s,
                    is_mortgage=%s,
                    monthly_payment=%s,
                    annual_interest_rate=%s,
                    monthly_principal_amount=%s,
                    monthly_interest_amount=%s,
                    loan_type=%s,
                    total_repayment_amount=%s,
                    updated_at=NOW(),
                    updated_by=%s
                WHERE id=%s
                """,
                (
                    name,
                    bank_id,
                    bank_name,
                    principal_amount,
                    term_months,
                    start_date_value,
                    description,
                    status,
                    exclude_from_dashboard,
                    is_mortgage,
                    monthly_payment,
                    annual_interest_rate if is_mortgage else None,
                    monthly_principal_amount if is_mortgage else None,
                    monthly_interest_amount if is_mortgage else None,
                    loan_type,
                    total_repayment_amount if is_interest_bearing else None,
                    session.get("user_name"),
                    id,
                ),
            )
            conn.commit()
            invalidate_dashboard_cache()
            logger.info(
                "loan_details_update user=%s id=%s name=%s status=%s is_mortgage=%s exclude_from_dashboard=%s",
                session.get("user_name"),
                id,
                name,
                status,
                is_mortgage,
                exclude_from_dashboard,
            )
    return redirect(f"/loans/{id}")


@loans_bp.route("/loans/<int:id>/dashboard-visibility", methods=["POST"])
def loan_dashboard_visibility(id):
    exclude_from_dashboard = request.form.get("exclude_from_dashboard") == "on"
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE loans
                SET exclude_from_dashboard=%s, updated_at=NOW(), updated_by=%s
                WHERE id=%s
                """,
                (exclude_from_dashboard, session.get("user_name"), id),
            )
            conn.commit()
            invalidate_dashboard_cache()
            logger.info(
                "loan_dashboard_visibility_update user=%s id=%s exclude_from_dashboard=%s",
                session.get("user_name"),
                id,
                exclude_from_dashboard,
            )
    return redirect(f"/loans/{id}")


@loans_bp.route("/loans/<int:id>/delete", methods=["POST"])
def loan_delete(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE records
                SET loan_id=NULL,
                    is_loan_payment=FALSE,
                    loan_principal_amount=NULL,
                    loan_interest_amount=NULL,
                    updated_at=NOW(),
                    updated_by=%s
                WHERE loan_id=%s
                  AND type='expense'
                  AND is_loan_payment=TRUE
                """,
                (session.get("user_name"), id),
            )
            detached_payments = cur.rowcount
            cur.execute("DELETE FROM loans WHERE id=%s", (id,))
            deleted = cur.rowcount
            conn.commit()
            invalidate_dashboard_cache()
            logger.info(
                "loan_delete user=%s id=%s deleted=%s detached_payments=%s",
                session.get("user_name"),
                id,
                deleted,
                detached_payments,
            )
    return redirect("/loans")
