from datetime import datetime
import logging
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
from flask import Blueprint, render_template, request, redirect, session

from db import get_db


movements_bp = Blueprint("movements", __name__)
logger = logging.getLogger("finance.movements")

PER_PAGE = 15
CONCEPT_RE = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\s\-\.,:/()&'+]+$")


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


def _parse_year_month(value, fallback):
    try:
        return datetime.strptime(value, "%Y-%m")
    except Exception:
        return fallback


def _validate_concept(value):
    concept = (value or "").strip()
    if not concept:
        return None, "Concept is required."
    if not CONCEPT_RE.fullmatch(concept):
        return None, "Concept contains invalid characters. Allowed: letters, numbers, spaces and . , - / ( ) : & ' +"
    return concept, None


def _validate_amount(value):
    try:
        amount = Decimal((value or "").strip())
    except (InvalidOperation, AttributeError):
        return None, "Amount must be a valid number."
    if amount <= 0:
        return None, "Amount must be greater than 0."
    return amount, None


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

    f_concept = request.args.get("concept", "")
    f_date = request.args.get("date", "")
    f_type = fixed_type or request.args.get("type", "")
    f_source = request.args.get("source", "")
    f_financed = request.args.get("financed", "")
    f_category = request.args.get("category", "")
    f_payment_method = request.args.get("payment_method_id", "")
    try:
        f_payment_method_int = int(f_payment_method) if f_payment_method else None
    except ValueError:
        f_payment_method_int = None

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
    if f_financed in ("1", "0"):
        base += " AND records.is_financed=%s"
        params.append(f_financed == "1")
    if f_category:
        base += " AND categories.name ILIKE %s"
        params.append(f"%{f_category}%")
    if f_payment_method_int is not None:
        base += " AND records.payment_method_id=%s"
        params.append(f_payment_method_int)

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
                       records.is_financed
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
        f_financed=f_financed,
        f_category=f_category,
        f_payment_method=str(f_payment_method_int) if f_payment_method_int is not None else "",
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
    if request.method == "POST":
        type_ = request.form["type"]
        source = request.form.get("source")

        if type_ != "expense":
            source = None

        months = request.form.getlist("months")
        date_fallback = request.form.get("date") or datetime.now().strftime("%Y-%m")
        is_deferred = (request.form.get("is_deferred") == "1")
        is_financed = (request.form.get("is_financed") == "1")
        try:
            deferred_total = int(request.form.get("deferred_total") or "1")
        except ValueError:
            deferred_total = 1
        deferred_total = min(max(deferred_total, 1), 60)
        if type_ != "expense":
            is_financed = False

        concept, concept_error = _validate_concept(request.form.get("concept"))
        if concept_error:
            return redirect(f"/records/add?from={from_page}&error={quote(concept_error)}")
        amount, amount_error = _validate_amount(request.form.get("amount"))
        if amount_error:
            return redirect(f"/records/add?from={from_page}&error={quote(amount_error)}")

        with get_db() as conn:
            with conn.cursor() as cur:
                comment = request.form.get("comment") or None
                category_name = request.form.get("category") or None
                category_id = _resolve_category_id(cur, category_name)
                payment_method_id = _resolve_payment_method_id(cur, request.form.get("payment_method_id"))
                if type_ != "expense":
                    payment_method_id = None

                deferred_dates = []
                if type_ == "expense" and is_deferred and deferred_total > 1:
                    base_dt = _parse_year_month(date_fallback, datetime.now())
                    deferred_dates = [_shift_month(base_dt, i).strftime("%Y-%m") for i in range(deferred_total)]
                dates = deferred_dates if deferred_dates else (months if months else [date_fallback])

                for idx, date_value in enumerate(dates, start=1):
                    deferred_index = idx if deferred_dates else None
                    deferred_total_value = deferred_total if deferred_dates else None
                    cur.execute("""
                    INSERT INTO records (concept, amount, date, type, source, comment, category_id, payment_method_id, is_financed, deferred_index, deferred_total, created_by, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    concept,
                    amount,
                    date_value,
                    type_,
                    source,
                    comment,
                    category_id,
                    payment_method_id,
                    is_financed,
                    deferred_index,
                    deferred_total_value,
                    session.get("user_name")
                ))
                conn.commit()
                logger.info(
                    "record_create user=%s type=%s from=%s concept=%s count=%s",
                    session.get("user_name"),
                    type_,
                    from_page,
                    concept,
                    len(dates),
                )

        return redirect(_page_to_url(from_page))

    year_now = datetime.now().year
    years = [year_now, year_now + 1]
    current_month = datetime.now().strftime("%Y-%m")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id, name FROM payment_methods WHERE is_active=TRUE ORDER BY name")
            payment_methods = cur.fetchall()
    return render_template(
        "add_movement.html",
        current_page=from_page,
        years=years,
        from_page=from_page,
        categories=categories,
        payment_methods=payment_methods,
        current_month=current_month,
        error=request.args.get("error")
    )


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
                       e.deferred_index, e.deferred_total, e.is_financed
                FROM records e
                LEFT JOIN categories c ON e.category_id = c.id
                LEFT JOIN payment_methods pm ON e.payment_method_id = pm.id
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
                    SELECT concept, amount, source, category_id, payment_method_id, deferred_index, deferred_total, type, is_financed
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
                concept, concept_error = _validate_concept(request.form.get("concept"))
                if concept_error:
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(concept_error)}")
                amount, amount_error = _validate_amount(request.form.get("amount"))
                if amount_error:
                    return redirect(f"/edit/{id}?from={from_page}&error={quote(amount_error)}")
                comment = request.form.get("comment") or None
                category_name = request.form.get("category") or None
                category_id = _resolve_category_id(cur, category_name)
                payment_method_id = _resolve_payment_method_id(cur, request.form.get("payment_method_id"))
                if type_ != "expense":
                    payment_method_id = None
                is_financed = (request.form.get("is_financed") == "1")
                if type_ != "expense":
                    is_financed = False
                is_deferred = (request.form.get("is_deferred") == "1")
                try:
                    deferred_total = int(request.form.get("deferred_total") or "1")
                except ValueError:
                    deferred_total = 1
                deferred_total = min(max(deferred_total, 1), 60)
                deferred_scope = (request.form.get("deferred_scope") or "single").strip().lower()
                deferred_index = 1 if (type_ == "expense" and is_deferred and deferred_total > 1) else None
                deferred_total_value = deferred_total if deferred_index else None
                date_value = request.form.get("date") or datetime.now().strftime("%Y-%m")

                prev_concept, prev_amount, prev_source, prev_category_id, prev_payment_method_id, prev_deferred_index, prev_deferred_total, prev_type, prev_is_financed = previous_record
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
                        category_id=%s, payment_method_id=%s, is_financed=%s, deferred_index=%s, deferred_total=%s, updated_at=NOW(), updated_by=%s
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
                    is_financed,
                    deferred_index,
                    deferred_total_value,
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
                          AND is_financed IS NOT DISTINCT FROM %s
                          AND COALESCE(deferred_index, 0) > %s
                        """,
                        (
                            id,
                            prev_concept,
                            prev_amount,
                            prev_source,
                            prev_category_id,
                            prev_payment_method_id,
                            prev_is_financed,
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
                            is_financed=%s,
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
                          AND is_financed IS NOT DISTINCT FROM %s
                        """,
                        (
                            concept,
                            amount,
                            source,
                            comment,
                            category_id,
                            payment_method_id,
                            is_financed,
                            deferred_total,
                            session.get("user_name"),
                            id,
                            deferred_total,
                            prev_concept,
                            prev_amount,
                            prev_source,
                            prev_category_id,
                            prev_payment_method_id,
                            prev_is_financed,
                        ),
                    )

                if deferred_index and deferred_total > 1:
                    base_dt = _parse_year_month(date_value, datetime.now())
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
                                    concept, amount, date, type, source, comment, category_id, payment_method_id, is_financed,
                                    deferred_index, deferred_total, created_by, created_at, updated_at
                                )
                                VALUES (%s, %s, %s, 'expense', %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                """,
                                (
                                    concept,
                                    amount,
                                    next_date,
                                    source,
                                    comment,
                                    category_id,
                                    payment_method_id,
                                    is_financed,
                                    installment_idx,
                                    deferred_total,
                                    session.get("user_name"),
                                ),
                            )

                conn.commit()
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
                       e.payment_method_id, e.deferred_index, e.deferred_total, e.is_financed
                FROM records e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.id=%s
            """, (id,))
            expense = cur.fetchone()
            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id, name, is_active FROM payment_methods ORDER BY name")
            payment_methods = cur.fetchall()

    return render_template(
        "edit.html",
        expense=expense,
        current_page=from_page,
        from_page=from_page,
        categories=categories,
        payment_methods=payment_methods,
        error=request.args.get("error")
    )


@movements_bp.route("/duplicate/<int:id>", methods=["GET", "POST"])
def duplicate(id):
    from_page = (request.args.get("from") or request.form.get("from") or "expense").strip()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id, e.concept, e.amount, e.date, e.type, e.source, e.comment,
                       c.name AS category_display,
                       e.category_id,
                       e.created_by, e.created_at, e.updated_at, e.updated_by,
                       e.payment_method_id, e.deferred_index, e.deferred_total, e.is_financed
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
                return redirect(f"/records/{id}?from={from_page}&error={quote(msg)}")

            if request.method == "POST":
                type_ = request.form["type"]
                source = request.form.get("source")

                if type_ != "expense":
                    source = None

                months = request.form.getlist("months")
                concept, concept_error = _validate_concept(request.form.get("concept"))
                if concept_error:
                    return redirect(f"/duplicate/{id}?from={from_page}&error={quote(concept_error)}")
                amount, amount_error = _validate_amount(request.form.get("amount"))
                if amount_error:
                    return redirect(f"/duplicate/{id}?from={from_page}&error={quote(amount_error)}")
                comment = request.form.get("comment") or None
                category_name = request.form.get("category") or None
                category_id = _resolve_category_id(cur, category_name)
                payment_method_id = _resolve_payment_method_id(cur, request.form.get("payment_method_id"))
                if type_ != "expense":
                    payment_method_id = None
                is_financed = (request.form.get("is_financed") == "1")
                if type_ != "expense":
                    is_financed = False
                date_fallback = request.form.get("date") or datetime.now().strftime("%Y-%m")
                is_deferred = (request.form.get("is_deferred") == "1")
                try:
                    deferred_total = int(request.form.get("deferred_total") or "1")
                except ValueError:
                    deferred_total = 1
                deferred_total = min(max(deferred_total, 1), 60)

                deferred_dates = []
                if type_ == "expense" and is_deferred and deferred_total > 1:
                    base_dt = _parse_year_month(date_fallback, datetime.now())
                    deferred_dates = [_shift_month(base_dt, i).strftime("%Y-%m") for i in range(deferred_total)]
                dates = deferred_dates if deferred_dates else (months if months else [date_fallback])

                for idx, date_value in enumerate(dates, start=1):
                    deferred_index = idx if deferred_dates else None
                    deferred_total_value = deferred_total if deferred_dates else None
                    cur.execute("""
                        INSERT INTO records (concept, amount, date, type, source, comment, category_id, payment_method_id, is_financed, deferred_index, deferred_total, created_by, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (
                        concept,
                        amount,
                        date_value,
                        type_,
                        source,
                        comment,
                        category_id,
                        payment_method_id,
                        is_financed,
                        deferred_index,
                        deferred_total_value,
                        session.get("user_name")
                    ))
                conn.commit()
                logger.info(
                    "record_duplicate user=%s source_id=%s type=%s from=%s concept=%s count=%s",
                    session.get("user_name"),
                    id,
                    type_,
                    from_page,
                    concept,
                    len(dates),
                )

                return redirect(_page_to_url(from_page))

    year_now = datetime.now().year
    years = [year_now, year_now + 1]
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM categories ORDER BY name")
            categories = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id, name, is_active FROM payment_methods ORDER BY name")
            payment_methods = cur.fetchall()
    return render_template(
        "duplicate.html",
        expense=expense,
        years=years,
        current_page=from_page,
        from_page=from_page,
        categories=categories,
        payment_methods=payment_methods,
        error=request.args.get("error")
    )


@movements_bp.route("/delete/<int:id>")
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
            cur.execute("DELETE FROM records WHERE id=%s", (id,))
            deleted = cur.rowcount
            conn.commit()
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
            logger.info("records_delete_all user=%s deleted=%s", session.get("user_name"), deleted)

    return redirect("/records/expense")
