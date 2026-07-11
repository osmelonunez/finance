from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging
from urllib.parse import quote
from flask import Blueprint, render_template, request, redirect, session

from db import get_db
from dashboard_cache import invalidate_dashboard_cache
from validators import (
    MAX_RECORD_COMMENT_LENGTH,
    parse_year_month,
    validate_amount,
    validate_concept,
    validate_text_length,
)


movements_bp = Blueprint("movements", __name__)
logger = logging.getLogger("finance.movements")

PER_PAGE = 15


def _shift_month(dt, months):
    idx = (dt.year * 12 + (dt.month - 1)) + months
    year = idx // 12
    month = idx % 12 + 1
    return dt.replace(year=year, month=month, day=1)


def _resolve_category_id(cur, name):
    if not name:
        return None
    cur.execute("SELECT id FROM categories WHERE name=%s", (name,))
    row = cur.fetchone()
    return row[0] if row else None

def _resolve_payment_method_id(cur, raw_id):
    if not raw_id:
        return None
    try:
        pm_id = int(raw_id)
    except (TypeError, ValueError):
        return None
    cur.execute("SELECT id FROM payment_methods WHERE id=%s", (pm_id,))
    row = cur.fetchone()
    return row[0] if row else None


def _resolve_active_loan_id(cur, raw_id, include_id=None):
    if not raw_id:
        return None
    try:
        loan_id = int(raw_id)
    except (TypeError, ValueError):
        return None
    if include_id and loan_id == include_id:
        cur.execute("SELECT id FROM loans WHERE id=%s AND status IN ('active', 'paid')", (loan_id,))
    else:
        cur.execute("SELECT id FROM loans WHERE id=%s AND status='active'", (loan_id,))
    row = cur.fetchone()
    return row[0] if row else None


def _load_loan_profile(cur, loan_id):
    if not loan_id:
        return None
    cur.execute(
        """
        SELECT id, is_mortgage, monthly_principal_amount, monthly_interest_amount
        FROM loans
        WHERE id=%s
        """,
        (loan_id,),
    )
    return cur.fetchone()


def _parse_non_negative_decimal(value, field_name):
    try:
        amount = Decimal((value or "").strip())
    except (InvalidOperation, AttributeError):
        return None, f"{field_name} must be a valid number."
    if amount < 0:
        return None, f"{field_name} must be greater than or equal to 0."
    return amount, None


def _parse_loan_payment_split(cur, loan_id, amount, form):
    profile = _load_loan_profile(cur, loan_id)
    if not profile or not profile[1]:
        return None, None, None

    principal, principal_error = validate_amount(form.get("loan_principal_amount"))
    if principal_error:
        return None, None, principal_error.replace("Amount", "Principal")

    interest, interest_error = _parse_non_negative_decimal(
        form.get("loan_interest_amount"),
        "Interest",
    )
    if interest_error:
        return None, None, interest_error

    if principal + interest != amount:
        return None, None, "Principal and interest must match amount."

    return principal, interest, None


def _load_active_loans(cur, include_id=None):
    params = []
    where = "l.status='active'"
    if include_id:
        where = "(l.status='active' OR l.id=%s)"
        params.append(include_id)
    cur.execute(
        f"""
        SELECT
            l.id,
            l.name,
            COALESCE(b.name, l.bank_name),
            l.is_mortgage,
            l.monthly_principal_amount,
            l.monthly_interest_amount
        FROM loans l
        LEFT JOIN banks b ON l.bank_id = b.id
        WHERE {where}
        ORDER BY l.name, COALESCE(b.name, l.bank_name)
        """,
        params,
    )
    return cur.fetchall()


def _sync_loan_statuses(cur, loan_ids):
    ids = {loan_id for loan_id in loan_ids if loan_id}
    for loan_id in ids:
        cur.execute(
            """
            WITH paid AS (
                SELECT COALESCE(SUM(amount), 0) AS paid_amount
                FROM records
                WHERE loan_id=%s
                  AND type='expense'
                  AND is_loan_payment=TRUE
            )
            UPDATE loans l
            SET status = CASE
                    WHEN paid.paid_amount >= COALESCE(l.total_repayment_amount, l.principal_amount) THEN 'paid'
                    WHEN l.status = 'paid' AND paid.paid_amount < COALESCE(l.total_repayment_amount, l.principal_amount) THEN 'active'
                    ELSE l.status
                END,
                exclude_from_dashboard = CASE
                    WHEN paid.paid_amount >= COALESCE(l.total_repayment_amount, l.principal_amount) THEN TRUE
                    ELSE l.exclude_from_dashboard
                END,
                updated_at = CASE
                    WHEN (
                        (paid.paid_amount >= COALESCE(l.total_repayment_amount, l.principal_amount) AND l.status <> 'paid')
                        OR (l.status = 'paid' AND paid.paid_amount < COALESCE(l.total_repayment_amount, l.principal_amount))
                    ) THEN NOW()
                    ELSE l.updated_at
                END,
                updated_by = CASE
                    WHEN (
                        (paid.paid_amount >= COALESCE(l.total_repayment_amount, l.principal_amount) AND l.status <> 'paid')
                        OR (l.status = 'paid' AND paid.paid_amount < COALESCE(l.total_repayment_amount, l.principal_amount))
                    ) THEN %s
                    ELSE l.updated_by
                END
            FROM paid
            WHERE l.id=%s
              AND l.status <> 'cancelled'
            """,
            (loan_id, session.get("user_name"), loan_id),
        )


def _records(fixed_type=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(per_page, %s) FROM users WHERE id=%s",
                (PER_PAGE, session.get("user_id")),
            )
            row = cur.fetchone()
            per_page = int(row[0]) if row else PER_PAGE
            cur.execute(
                "SELECT COALESCE(value,1) FROM settings WHERE key='records_years'"
            )
            row = cur.fetchone()
            records_years = int(row[0]) if row else 1
            records_years = min(max(records_years, 1), 10)

            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id, name FROM payment_methods ORDER BY name")
            payment_methods = cur.fetchall()
            loans = _load_active_loans(cur)

    f_concept = request.args.get("concept", "")
    f_date = request.args.get("date", "")
    f_type = fixed_type or request.args.get("type", "")
    f_source = request.args.get("source", "")
    f_category = request.args.get("category", "")
    f_payment_method = request.args.get("payment_method_id", "")
    f_loan = request.args.get("loan_id", "")
    try:
        f_payment_method_int = int(f_payment_method) if f_payment_method else None
    except ValueError:
        f_payment_method_int = None
    try:
        f_loan_int = int(f_loan) if f_loan else None
    except ValueError:
        f_loan_int = None

    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")

    page = int(request.args.get("page", 1))
    offset = (page - 1) * per_page

    allowed_sort = {
        "concept": "records.concept",
        "amount": "records.amount",
        "date": "records.date",
        "type": "records.type",
        "category": "categories.name"
    }

    sort_column = allowed_sort.get(sort, "date")
    order_sql = "ASC" if order == "asc" else "DESC"

    base = """
    FROM records
    LEFT JOIN categories ON records.category_id = categories.id
    LEFT JOIN payment_methods ON records.payment_method_id = payment_methods.id
    LEFT JOIN loans ON records.loan_id = loans.id
    WHERE 1=1
    """
    params = []
    month_now = datetime.now().replace(day=1)
    min_month = _shift_month(month_now, -(records_years * 12 - 1)).strftime("%Y-%m")

    base += " AND date >= %s"
    params.append(min_month)

    if f_concept:
        base += " AND concept ILIKE %s"
        params.append(f"%{f_concept}%")
    if f_date:
        base += " AND date=%s"
        params.append(f_date)
    if f_type:
        base += " AND type=%s"
        params.append(f_type)
    if f_source:
        base += " AND source=%s"
        params.append(f_source)
    if f_category:
        base += " AND categories.name ILIKE %s"
        params.append(f"%{f_category}%")
    if f_payment_method_int is not None:
        base += " AND records.payment_method_id=%s"
        params.append(f_payment_method_int)
    if f_loan_int is not None:
        base += " AND records.loan_id=%s"
        params.append(f_loan_int)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT records.id,
                       CASE
                           WHEN records.deferred_total IS NOT NULL AND records.deferred_total > 1
                           THEN CONCAT(records.concept, ' (', COALESCE(records.deferred_index, 1), '/', records.deferred_total, ')')
                           ELSE records.concept
                       END AS concept,
                       records.amount, records.date, records.type, records.source, records.comment,
                       categories.name AS category_display,
                       payment_methods.name AS payment_method_display,
                       records.is_loan_payment,
                       loans.name AS loan_name,
                       loans.bank_name AS loan_bank_name
                {base}
                ORDER BY {sort_column} {order_sql}
                LIMIT %s OFFSET %s
                """,
                params + [per_page, offset]
            )
            expenses = cur.fetchall()

            cur.execute(
                f"SELECT COUNT(*) {base}",
                params
            )
            total = cur.fetchone()[0]

            cur.execute(
                f"""
                SELECT
                    COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),0),
                    COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END),0),
                    COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END),0)
                {base}
                """,
                params
            )
            totals = cur.fetchone()

            cur.execute(
                f"SELECT COALESCE(SUM(amount),0) {base}",
                params
            )
            total_amount = cur.fetchone()[0]

    total_income, total_expense, total_saving = totals
    total_balance = total_income - total_expense - total_saving
    total_pages = (total + per_page - 1) // per_page
    showing_from = (page - 1) * per_page + 1 if total > 0 else 0
    showing_to = min(page * per_page, total)

    show_bulk = request.args.get("select") == "1"

    query_params = request.args.to_dict(flat=True)
    query_params.pop("page", None)
    from urllib.parse import urlencode
    page_query = urlencode(query_params)

    return render_template(
        "movements.html",
        expenses=expenses,
        f_concept=f_concept,
        f_date=f_date,
        f_type=f_type,
        f_source=f_source,
        f_category=f_category,
        f_payment_method=str(f_payment_method_int) if f_payment_method_int is not None else "",
        f_loan=str(f_loan_int) if f_loan_int is not None else "",
        sort=sort,
        order=order,
        page=page,
        total_pages=total_pages,
        total_income=total_income,
        total_expense=total_expense,
        total_saving=total_saving,
        total_balance=total_balance,
        total_amount=total_amount,
        showing_from=showing_from,
        showing_to=showing_to,
        total=total,
        show_bulk=show_bulk,
        current_page=fixed_type or "records",
        fixed_type=fixed_type,
        return_to=request.full_path.rstrip("?"),
        categories=categories,
        payment_methods=payment_methods,
        loans=loans,
        page_query=page_query
    )


@movements_bp.route("/records/income")
def records_income():
    return _records("income")


@movements_bp.route("/records/expense")
def records_expense():
    return _records("expense")


@movements_bp.route("/records/saving")
def records_saving():
    return _records("saving")


def _page_to_url(page):
    return {
        "expense": "/records/expense",
        "income": "/records/income",
        "saving": "/records/saving"
    }.get(page, "/records/expense")


@movements_bp.route("/records/add", methods=["GET", "POST"])
def add_movement():
    from_page = (request.args.get("from") or request.form.get("from") or "expense").strip()
    year_now = datetime.now().year
    years = [year_now, year_now + 1]
    current_month = datetime.now().strftime("%Y-%m")

    def _load_add_dependencies():
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM categories ORDER BY name")
                categories = [r[0] for r in cur.fetchall()]
                cur.execute("SELECT id, name FROM payment_methods WHERE is_active=TRUE ORDER BY name")
                payment_methods = cur.fetchall()
                loans = _load_active_loans(cur)
        return categories, payment_methods, loans

    def _render_add(error=None, form_data=None):
        categories, payment_methods, loans = _load_add_dependencies()
        initial_form_data = dict(form_data or {})
        if request.method == "GET" and request.args.get("loan_id") and not initial_form_data:
            initial_form_data["loan_id"] = request.args.get("loan_id")
            initial_form_data["is_loan_payment"] = "1"
            initial_form_data["source"] = "monthly"
        return render_template(
            "add_movement.html",
            current_page=from_page,
            years=years,
            from_page=from_page,
            categories=categories,
            payment_methods=payment_methods,
            loans=loans,
            current_month=current_month,
            error=error,
            form_data=initial_form_data
        )

    if request.method == "POST":
        type_ = request.form["type"]
        source = request.form.get("source")

        if type_ != "expense":
            source = None

        months = request.form.getlist("months")
        date_fallback = request.form.get("date") or datetime.now().strftime("%Y-%m")
        is_deferred = (request.form.get("is_deferred") == "1")
        is_loan_payment = (request.form.get("is_loan_payment") == "1")
        try:
            deferred_total = int(request.form.get("deferred_total") or "1")
        except ValueError:
            deferred_total = 1
        deferred_total = min(max(deferred_total, 1), 60)
        if type_ != "expense":
            is_loan_payment = False
        if is_loan_payment:
            is_deferred = False

        concept, concept_error = validate_concept(request.form.get("concept"))
        if concept_error:
            return _render_add(
                error=concept_error,
                form_data=request.form.to_dict(flat=True) | {"months": request.form.getlist("months")},
            )
        amount, amount_error = validate_amount(request.form.get("amount"))
        if amount_error:
            return _render_add(
                error=amount_error,
                form_data=request.form.to_dict(flat=True) | {"months": request.form.getlist("months")},
            )

        with get_db() as conn:
            with conn.cursor() as cur:
                comment, comment_error = validate_text_length(
                    request.form.get("comment"),
                    "Comment",
                    MAX_RECORD_COMMENT_LENGTH,
                )
                if comment_error:
                    return _render_add(
                        error=comment_error,
                        form_data=request.form.to_dict(flat=True) | {"months": request.form.getlist("months")},
                    )
                category_name = request.form.get("category") or None
                category_id = _resolve_category_id(cur, category_name)
                payment_method_id = _resolve_payment_method_id(cur, request.form.get("payment_method_id"))
                if type_ != "expense":
                    payment_method_id = None
                loan_id = _resolve_active_loan_id(cur, request.form.get("loan_id")) if is_loan_payment else None
                if is_loan_payment and loan_id is None:
                    return _render_add(
                        error="Select an active loan.",
                        form_data=request.form.to_dict(flat=True) | {"months": request.form.getlist("months")},
                    )
                loan_principal_amount, loan_interest_amount, split_error = _parse_loan_payment_split(
                    cur,
                    loan_id,
                    amount,
                    request.form,
                ) if is_loan_payment else (None, None, None)
                if split_error:
                    return _render_add(
                        error=split_error,
                        form_data=request.form.to_dict(flat=True) | {"months": request.form.getlist("months")},
                    )

                deferred_dates = []
                if type_ == "expense" and is_deferred and deferred_total > 1:
                    base_dt = parse_year_month(date_fallback, datetime.now())
                    deferred_dates = [_shift_month(base_dt, i).strftime("%Y-%m") for i in range(deferred_total)]
                dates = deferred_dates if deferred_dates else (months if months else [date_fallback])

                for idx, date_value in enumerate(dates, start=1):
                    deferred_index = idx if deferred_dates else None
                    deferred_total_value = deferred_total if deferred_dates else None
                    cur.execute("""
                    INSERT INTO records (
                        concept, amount, date, type, source, comment, category_id, payment_method_id,
                        deferred_index, deferred_total, loan_id, is_loan_payment,
                        loan_principal_amount, loan_interest_amount, created_by, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    concept,
                    amount,
                    date_value,
                    type_,
                    source,
                    comment,
                    category_id,
                    payment_method_id,
                    deferred_index,
                    deferred_total_value,
                    loan_id,
                    is_loan_payment,
                    loan_principal_amount,
                    loan_interest_amount,
                    session.get("user_name")
                ))
                _sync_loan_statuses(cur, [loan_id])
                conn.commit()
                invalidate_dashboard_cache()
                logger.info(
                    "record_create user=%s type=%s from=%s concept=%s count=%s",
                    session.get("user_name"),
                    type_,
                    from_page,
                    concept,
                    len(dates),
                )

        return redirect(_page_to_url(from_page))

    return _render_add(error=request.args.get("error"))


@movements_bp.route("/records/<int:id>")
def movement_detail(id):
    from_page = (request.args.get("from") or "expense").strip()
    return_to = (request.args.get("return_to") or "").strip()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id, e.concept, e.amount, e.date, e.type, e.source, e.comment,
                       c.name AS category_display,
                       e.created_by, e.created_at, e.updated_at, e.updated_by,
                       e.payment_method_id, pm.name AS payment_method_name,
                       e.deferred_index, e.deferred_total,
                       e.loan_id, e.is_loan_payment, l.name AS loan_name, l.bank_name AS loan_bank_name,
                       e.loan_principal_amount, e.loan_interest_amount
                FROM records e
                LEFT JOIN categories c ON e.category_id = c.id
                LEFT JOIN payment_methods pm ON e.payment_method_id = pm.id
                LEFT JOIN loans l ON e.loan_id = l.id
                WHERE e.id=%s
            """, (id,))
            expense = cur.fetchone()

    if not expense:
        return redirect(_page_to_url(from_page))

    return render_template(
        "movement_detail.html",
        expense=expense,
        current_page=from_page,
        from_page=from_page,
        return_to=return_to,
        error=request.args.get("error")
    )


@movements_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    from_page = (request.args.get("from") or request.form.get("from") or "expense").strip()
    with get_db() as conn:
        with conn.cursor() as cur:
            if request.method == "POST":
                cur.execute(
                    """
                    SELECT concept, amount, source, category_id, payment_method_id, deferred_index, deferred_total, type, loan_id, is_loan_payment
                    FROM records
                    WHERE id=%s
                    """,
                    (id,),
                )
                previous_record = cur.fetchone()
                if not previous_record:
                    return redirect(_page_to_url(from_page))

                type_ = request.form["type"]
                source = request.form.get("source")

                if type_ != "expense":
                    source = None

                concept = request.form["concept"]
                concept, concept_error = validate_concept(request.form.get("concept"))
                if concept_error:
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(concept_error)}")
                amount, amount_error = validate_amount(request.form.get("amount"))
                if amount_error:
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(amount_error)}")
                comment, comment_error = validate_text_length(
                    request.form.get("comment"),
                    "Comment",
                    MAX_RECORD_COMMENT_LENGTH,
                )
                if comment_error:
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(comment_error)}")
                category_name = request.form.get("category") or None
                category_id = _resolve_category_id(cur, category_name)
                payment_method_id = _resolve_payment_method_id(cur, request.form.get("payment_method_id"))
                if type_ != "expense":
                    payment_method_id = None
                is_loan_payment = (request.form.get("is_loan_payment") == "1")
                if type_ != "expense":
                    is_loan_payment = False
                is_deferred = (request.form.get("is_deferred") == "1")
                if is_loan_payment:
                    is_deferred = False
                try:
                    deferred_total = int(request.form.get("deferred_total") or "1")
                except ValueError:
                    deferred_total = 1
                deferred_total = min(max(deferred_total, 1), 60)
                deferred_scope = (request.form.get("deferred_scope") or "single").strip().lower()
                deferred_index = 1 if (type_ == "expense" and is_deferred and deferred_total > 1) else None
                deferred_total_value = deferred_total if deferred_index else None
                date_value = request.form.get("date") or datetime.now().strftime("%Y-%m")

                prev_concept, prev_amount, prev_source, prev_category_id, prev_payment_method_id, prev_deferred_index, prev_deferred_total, prev_type, prev_loan_id, prev_is_loan_payment = previous_record
                loan_id = _resolve_active_loan_id(
                    cur,
                    request.form.get("loan_id"),
                    include_id=prev_loan_id,
                ) if is_loan_payment else None
                if is_loan_payment and loan_id is None:
                    msg = "Select an active loan."
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(msg)}")
                loan_principal_amount, loan_interest_amount, split_error = _parse_loan_payment_split(
                    cur,
                    loan_id,
                    amount,
                    request.form,
                ) if is_loan_payment else (None, None, None)
                if split_error:
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(split_error)}")

                if (
                    prev_type == "expense"
                    and (prev_deferred_total or 0) > 1
                    and (prev_deferred_index or 1) > 1
                    and (
                        not is_deferred
                        or deferred_total != (prev_deferred_total or 0)
                    )
                ):
                    msg = "Installments can only be changed from the first deferred record."
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(msg)}")

                should_clear_series = (
                    prev_type == "expense"
                    and (prev_deferred_total or 0) > 1
                    and not is_deferred
                    and deferred_scope in ("all", "series")
                )
                if should_clear_series:
                    cur.execute(
                        """
                        DELETE FROM records
                        WHERE id <> %s
                          AND type = 'expense'
                          AND concept = %s
                          AND amount = %s
                          AND source IS NOT DISTINCT FROM %s
                          AND category_id IS NOT DISTINCT FROM %s
                          AND payment_method_id IS NOT DISTINCT FROM %s
                          AND COALESCE(deferred_total, 0) = %s
                          AND deferred_index IS NOT NULL
                        """,
                        (
                            id,
                            prev_concept,
                            prev_amount,
                            prev_source,
                            prev_category_id,
                            prev_payment_method_id,
                            prev_deferred_total,
                        ),
                    )

                cur.execute("""
                    UPDATE records
                    SET concept=%s, amount=%s, date=%s, type=%s, source=%s, comment=%s,
                        category_id=%s, payment_method_id=%s, deferred_index=%s, deferred_total=%s,
                        loan_id=%s, is_loan_payment=%s, loan_principal_amount=%s, loan_interest_amount=%s,
                        updated_at=NOW(), updated_by=%s
                    WHERE id=%s
                """, (
                    concept,
                    amount,
                    date_value,
                    type_,
                    source,
                    comment,
                    category_id,
                    payment_method_id,
                    deferred_index,
                    deferred_total_value,
                    loan_id,
                    is_loan_payment,
                    loan_principal_amount,
                    loan_interest_amount,
                    session.get("user_name"),
                    id
                ))

                should_sync_series = (
                    type_ == "expense"
                    and is_deferred
                    and (prev_deferred_total or 0) > 1
                    and (prev_deferred_index or 1) == 1
                )
                if should_sync_series:
                    # Remove out-of-range siblings before updating deferred_total to avoid CHECK violations.
                    cur.execute(
                        """
                        DELETE FROM records
                        WHERE id <> %s
                          AND type = 'expense'
                          AND deferred_index IS NOT NULL
                          AND concept = %s
                          AND amount = %s
                          AND source IS NOT DISTINCT FROM %s
                          AND category_id IS NOT DISTINCT FROM %s
                          AND payment_method_id IS NOT DISTINCT FROM %s
                          AND loan_id IS NOT DISTINCT FROM %s
                          AND is_loan_payment IS NOT DISTINCT FROM %s
                          AND COALESCE(deferred_index, 0) > %s
                        """,
                        (
                            id,
                            prev_concept,
                            prev_amount,
                            prev_source,
                            prev_category_id,
                            prev_payment_method_id,
                            prev_loan_id,
                            prev_is_loan_payment,
                            deferred_total,
                        ),
                    )

                    # Keep remaining sibling installments aligned with edited main row.
                    cur.execute(
                        """
                        UPDATE records
                        SET concept=%s,
                            amount=%s,
                            source=%s,
                            comment=%s,
                            category_id=%s,
                            payment_method_id=%s,
                            loan_id=%s,
                            is_loan_payment=%s,
                            loan_principal_amount=%s,
                            loan_interest_amount=%s,
                            deferred_total=%s,
                            updated_at=NOW(),
                            updated_by=%s
                        WHERE id <> %s
                          AND type = 'expense'
                          AND deferred_index IS NOT NULL
                          AND COALESCE(deferred_index, 0) <= %s
                          AND concept = %s
                          AND amount = %s
                          AND source IS NOT DISTINCT FROM %s
                          AND category_id IS NOT DISTINCT FROM %s
                          AND payment_method_id IS NOT DISTINCT FROM %s
                          AND loan_id IS NOT DISTINCT FROM %s
                          AND is_loan_payment IS NOT DISTINCT FROM %s
                        """,
                        (
                            concept,
                            amount,
                            source,
                            comment,
                            category_id,
                            payment_method_id,
                            loan_id,
                            is_loan_payment,
                            loan_principal_amount,
                            loan_interest_amount,
                            deferred_total,
                            session.get("user_name"),
                            id,
                            deferred_total,
                            prev_concept,
                            prev_amount,
                            prev_source,
                            prev_category_id,
                            prev_payment_method_id,
                            prev_loan_id,
                            prev_is_loan_payment,
                        ),
                    )

                if deferred_index and deferred_total > 1:
                    base_dt = parse_year_month(date_value, datetime.now())
                    for installment_idx in range(2, deferred_total + 1):
                        next_date = _shift_month(base_dt, installment_idx - 1).strftime("%Y-%m")
                        cur.execute(
                            """
                            SELECT 1
                            FROM records
                            WHERE type='expense'
                              AND concept=%s
                              AND amount=%s
                              AND date=%s
                              AND COALESCE(deferred_index, 0)=%s
                              AND COALESCE(deferred_total, 0)=%s
                            LIMIT 1
                            """,
                            (concept, amount, next_date, installment_idx, deferred_total),
                        )
                        if not cur.fetchone():
                            cur.execute(
                                """
                                INSERT INTO records (
                                    concept, amount, date, type, source, comment, category_id, payment_method_id,
                                    deferred_index, deferred_total, loan_id, is_loan_payment,
                                    loan_principal_amount, loan_interest_amount, created_by, created_at, updated_at
                                )
                                VALUES (%s, %s, %s, 'expense', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                """,
                                (
                                    concept,
                                    amount,
                                    next_date,
                                    source,
                                    comment,
                                    category_id,
                                    payment_method_id,
                                    installment_idx,
                                    deferred_total,
                                    loan_id,
                                    is_loan_payment,
                                    loan_principal_amount,
                                    loan_interest_amount,
                                    session.get("user_name"),
                                ),
                            )

                _sync_loan_statuses(cur, [prev_loan_id, loan_id])
                conn.commit()
                invalidate_dashboard_cache()
                logger.info(
                    "record_update user=%s id=%s type=%s from=%s concept=%s",
                    session.get("user_name"),
                    id,
                    type_,
                    from_page,
                    concept,
                )

                return redirect(_page_to_url(from_page))

            cur.execute("""
                SELECT e.id, e.concept, e.amount, e.date, e.type, e.source, e.comment,
                       c.name AS category_display,
                       e.category_id,
                       e.created_by, e.created_at, e.updated_at, e.updated_by,
                       e.payment_method_id, e.deferred_index, e.deferred_total,
                       e.loan_id, e.is_loan_payment, e.loan_principal_amount, e.loan_interest_amount
                FROM records e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.id=%s
            """, (id,))
            expense = cur.fetchone()
            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id, name, is_active FROM payment_methods ORDER BY name")
            payment_methods = cur.fetchall()
            loans = _load_active_loans(cur, include_id=expense[16] if expense else None)

    return render_template(
        "edit.html",
        expense=expense,
        current_page=from_page,
        from_page=from_page,
        categories=categories,
        payment_methods=payment_methods,
        loans=loans,
        error=request.args.get("error")
    )


@movements_bp.route("/duplicate/<int:id>", methods=["GET", "POST"])
def duplicate(id):
    from_page = (request.args.get("from") or request.form.get("from") or "expense").strip()
    return_to = (request.args.get("return_to") or request.form.get("return_to") or "").strip()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id, e.concept, e.amount, e.date, e.type, e.source, e.comment,
                       c.name AS category_display,
                       e.category_id,
                       e.created_by, e.created_at, e.updated_at, e.updated_by,
                       e.payment_method_id, e.deferred_index, e.deferred_total,
                       e.loan_id, e.is_loan_payment, e.loan_principal_amount, e.loan_interest_amount
                FROM records e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.id=%s
            """, (id,))
            expense = cur.fetchone()
            if not expense:
                return redirect(_page_to_url(from_page))

            is_deferred_record = bool((expense[15] or 0) > 1)
            if is_deferred_record:
                msg = "Deferred payment records cannot be duplicated."
                detail_url = f"/records/{id}?from={from_page}&error={quote(msg)}"
                if return_to.startswith("/"):
                    detail_url += f"&return_to={quote(return_to)}"
                return redirect(detail_url)

            if request.method == "POST":
                type_ = request.form["type"]
                source = request.form.get("source")

                if type_ != "expense":
                    source = None

                months = request.form.getlist("months")
                concept, concept_error = validate_concept(request.form.get("concept"))
                if concept_error:
                    duplicate_url = f"/duplicate/{id}?from={from_page}&error={quote(concept_error)}"
                    if return_to.startswith("/"):
                        duplicate_url += f"&return_to={quote(return_to)}"
                    return redirect(duplicate_url)
                amount, amount_error = validate_amount(request.form.get("amount"))
                if amount_error:
                    duplicate_url = f"/duplicate/{id}?from={from_page}&error={quote(amount_error)}"
                    if return_to.startswith("/"):
                        duplicate_url += f"&return_to={quote(return_to)}"
                    return redirect(duplicate_url)
                comment, comment_error = validate_text_length(
                    request.form.get("comment"),
                    "Comment",
                    MAX_RECORD_COMMENT_LENGTH,
                )
                if comment_error:
                    duplicate_url = f"/duplicate/{id}?from={from_page}&error={quote(comment_error)}"
                    if return_to.startswith("/"):
                        duplicate_url += f"&return_to={quote(return_to)}"
                    return redirect(duplicate_url)
                category_name = request.form.get("category") or None
                category_id = _resolve_category_id(cur, category_name)
                payment_method_id = _resolve_payment_method_id(cur, request.form.get("payment_method_id"))
                if type_ != "expense":
                    payment_method_id = None
                is_loan_payment = (request.form.get("is_loan_payment") == "1")
                if type_ != "expense":
                    is_loan_payment = False
                date_fallback = request.form.get("date") or datetime.now().strftime("%Y-%m")
                is_deferred = (request.form.get("is_deferred") == "1")
                if is_loan_payment:
                    is_deferred = False
                try:
                    deferred_total = int(request.form.get("deferred_total") or "1")
                except ValueError:
                    deferred_total = 1
                deferred_total = min(max(deferred_total, 1), 60)

                deferred_dates = []
                loan_id = _resolve_active_loan_id(cur, request.form.get("loan_id")) if is_loan_payment else None
                if is_loan_payment and loan_id is None:
                    duplicate_url = f"/duplicate/{id}?from={from_page}&error={quote('Select an active loan.')}"
                    if return_to.startswith("/"):
                        duplicate_url += f"&return_to={quote(return_to)}"
                    return redirect(duplicate_url)
                loan_principal_amount, loan_interest_amount, split_error = _parse_loan_payment_split(
                    cur,
                    loan_id,
                    amount,
                    request.form,
                ) if is_loan_payment else (None, None, None)
                if split_error:
                    duplicate_url = f"/duplicate/{id}?from={from_page}&error={quote(split_error)}"
                    if return_to.startswith("/"):
                        duplicate_url += f"&return_to={quote(return_to)}"
                    return redirect(duplicate_url)
                if type_ == "expense" and is_deferred and deferred_total > 1:
                    base_dt = parse_year_month(date_fallback, datetime.now())
                    deferred_dates = [_shift_month(base_dt, i).strftime("%Y-%m") for i in range(deferred_total)]
                dates = deferred_dates if deferred_dates else (months if months else [date_fallback])

                for idx, date_value in enumerate(dates, start=1):
                    deferred_index = idx if deferred_dates else None
                    deferred_total_value = deferred_total if deferred_dates else None
                    cur.execute("""
                        INSERT INTO records (
                            concept, amount, date, type, source, comment, category_id, payment_method_id,
                            deferred_index, deferred_total, loan_id, is_loan_payment,
                            loan_principal_amount, loan_interest_amount, created_by, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (
                        concept,
                        amount,
                        date_value,
                        type_,
                        source,
                        comment,
                        category_id,
                        payment_method_id,
                        deferred_index,
                        deferred_total_value,
                        loan_id,
                        is_loan_payment,
                        loan_principal_amount,
                        loan_interest_amount,
                        session.get("user_name")
                    ))
                _sync_loan_statuses(cur, [loan_id])
                conn.commit()
                invalidate_dashboard_cache()
                logger.info(
                    "record_duplicate user=%s source_id=%s type=%s from=%s concept=%s count=%s",
                    session.get("user_name"),
                    id,
                    type_,
                    from_page,
                    concept,
                    len(dates),
                )

                if return_to.startswith("/"):
                    return redirect(return_to)
                return redirect(_page_to_url(from_page))

    record_dt = parse_year_month(expense[3], datetime.now())
    record_year = record_dt.year
    years = [record_year - 1, record_year, record_year + 1]
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id, name, is_active FROM payment_methods ORDER BY name")
            payment_methods = cur.fetchall()
            loans = _load_active_loans(cur)
    return render_template(
        "duplicate.html",
        expense=expense,
        years=years,
        current_page=from_page,
        from_page=from_page,
        return_to=return_to,
        categories=categories,
        payment_methods=payment_methods,
        loans=loans,
        error=request.args.get("error")
    )


@movements_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    from_page = (request.args.get("from") or "").strip()
    return_to = (request.args.get("return_to") or "").strip()
    redirect_map = {
        "expense": "/records/expense",
        "income": "/records/income",
        "saving": "/records/saving"
    }
    target = redirect_map.get(from_page, "/records/expense")
    if return_to.startswith("/"):
        target = return_to
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT loan_id FROM records WHERE id=%s AND type='expense' AND is_loan_payment=TRUE",
                (id,),
            )
            row = cur.fetchone()
            loan_id = row[0] if row else None
            cur.execute("DELETE FROM records WHERE id=%s", (id,))
            deleted = cur.rowcount
            _sync_loan_statuses(cur, [loan_id])
            conn.commit()
            invalidate_dashboard_cache()
            logger.info(
                "record_delete user=%s id=%s from=%s deleted=%s",
                session.get("user_name"),
                id,
                from_page,
                deleted,
            )

    return redirect(target)


@movements_bp.route("/delete-all", methods=["POST"])
def delete_all():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM records")
            deleted = cur.rowcount
            conn.commit()
            invalidate_dashboard_cache()
            logger.info("records_delete_all user=%s deleted=%s", session.get("user_name"), deleted)

    return redirect("/records/expense")
