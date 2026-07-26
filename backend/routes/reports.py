from datetime import datetime
from decimal import Decimal
import csv
import io
import re

from flask import Blueprint, Response, redirect, render_template, request, session, url_for

from db import get_db
from i18n import category_name
from report_service import _report_texts
from report_templates import _normalize_version, render_report_html
from validators import parse_year_month


reports_bp = Blueprint("reports", __name__)


def _positive_int(value):
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _report_filters(args):
    loan_value = (args.get("loan_id") or "").strip().lower()
    return {
        "category_id": _positive_int(args.get("category_id")),
        "bank_id": _positive_int(args.get("bank_id")),
        "account_id": _positive_int(args.get("account_id")),
        "card_id": _positive_int(args.get("card_id")),
        "loan_id": _positive_int(loan_value),
        "without_loan": loan_value == "none",
    }


def _filter_sql(filters, alias="r"):
    clauses, params = [], []
    if filters and filters.get("category_id"):
        clauses.append(f"{alias}.category_id=%s")
        params.append(filters["category_id"])
    if filters and filters.get("bank_id"):
        clauses.append(
            f"{alias}.payment_method_id IN (SELECT id FROM payment_methods WHERE bank_id=%s)"
        )
        params.append(filters["bank_id"])
    if filters and filters.get("account_id"):
        clauses.append(
            f"{alias}.payment_method_id IN "
            "(SELECT id FROM payment_methods WHERE id=%s OR parent_account_id=%s)"
        )
        params.extend((filters["account_id"], filters["account_id"]))
    if filters and filters.get("card_id"):
        clauses.append(f"{alias}.payment_method_id=%s")
        params.append(filters["card_id"])
    if filters and filters.get("loan_id"):
        clauses.append(f"{alias}.loan_id=%s")
        params.append(filters["loan_id"])
    elif filters and filters.get("without_loan"):
        clauses.append(f"{alias}.loan_id IS NULL")
    return (" AND " + " AND ".join(clauses) if clauses else ""), params


def _report_config(cur):
    cur.execute(
        """
        SELECT monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version
        FROM email_report_config
        WHERE id=1
        """
    )
    row = cur.fetchone()
    if not row:
        return {
            "monthly_enabled": True,
            "yearly_enabled": True,
            "monthly_template_version": "v1",
            "yearly_template_version": "v1",
        }
    return {
        "monthly_enabled": bool(row[0]),
        "yearly_enabled": bool(row[1]),
        "monthly_template_version": _normalize_version(row[2]),
        "yearly_template_version": _normalize_version(row[3]),
    }


def _valid_period(report_type, raw_period):
    now = datetime.now()
    if report_type == "yearly":
        try:
            year = int(raw_period or now.year)
        except (TypeError, ValueError):
            year = now.year
        return str(min(max(year, 2000), now.year))
    parsed = parse_year_month(raw_period or "", now.replace(day=1))
    if parsed > now.replace(day=1):
        parsed = now.replace(day=1)
    return parsed.strftime("%Y-%m")


def _summary(cur, report_type, period, filters=None):
    if report_type == "yearly":
        start, end = f"{period}-01", f"{period}-12"
        where = "date >= %s AND date <= %s"
        params = (start, end)
    else:
        where = "date=%s"
        params = (period,)
    filter_sql, filter_params = _filter_sql(filters)
    cur.execute(
        f"""
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END), 0)
        FROM records r
        WHERE {where}{filter_sql}
        """,
        params + tuple(filter_params),
    )
    income, expense, saving = cur.fetchone()
    return {
        "income": Decimal(income or 0),
        "expense": Decimal(expense or 0),
        "saving": Decimal(saving or 0),
        "balance": Decimal(income or 0) - Decimal(expense or 0) - Decimal(saving or 0),
    }


def _summary_between(cur, start, end, filters=None):
    filter_sql, filter_params = _filter_sql(filters)
    cur.execute(
        f"""
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END), 0)
        FROM records r
        WHERE date >= %s AND date <= %s{filter_sql}
        """,
        (start, end, *filter_params),
    )
    income, expense, saving = (Decimal(value or 0) for value in cur.fetchone())
    return {
        "income": income,
        "expense": expense,
        "saving": saving,
        "balance": income - expense - saving,
    }


def _comparison_period(scope, raw_period, lang):
    now = datetime.now()
    if scope == "year":
        year = int(_valid_period("yearly", raw_period))
        return {
            "key": str(year),
            "current": (f"{year}-01", f"{year}-12"),
            "previous": (f"{year - 1}-01", f"{year - 1}-12"),
            "previous_key": str(year - 1),
            "current_label": str(year),
            "previous_label": str(year - 1),
        }
    if scope == "quarter":
        match = re.fullmatch(r"(\d{4})-Q([1-4])", raw_period or "")
        year, quarter = (int(match.group(1)), int(match.group(2))) if match else (now.year, ((now.month - 1) // 3) + 1)
        current_index = now.year * 4 + ((now.month - 1) // 3)
        selected_index = min(max(year * 4 + quarter - 1, 2000 * 4), current_index)
        year, quarter_index = divmod(selected_index, 4)
        quarter = quarter_index + 1
        previous_year, previous_index = divmod(selected_index - 1, 4)
        previous_quarter = previous_index + 1
        start_month = (quarter - 1) * 3 + 1
        previous_start = (previous_quarter - 1) * 3 + 1
        prefix = "T" if lang == "es" else "Q"
        return {
            "key": f"{year}-Q{quarter}",
            "current": (f"{year}-{start_month:02d}", f"{year}-{start_month + 2:02d}"),
            "previous": (f"{previous_year}-{previous_start:02d}", f"{previous_year}-{previous_start + 2:02d}"),
            "previous_key": f"{previous_year}-Q{previous_quarter}",
            "current_label": f"{year} {prefix}{quarter}",
            "previous_label": f"{previous_year} {prefix}{previous_quarter}",
        }
    month = _valid_period("monthly", raw_period)
    year, month_number = (int(value) for value in month.split("-"))
    previous_year, previous_month = (year - 1, 12) if month_number == 1 else (year, month_number - 1)
    return {
        "key": month,
        "current": (month, month),
        "previous": (f"{previous_year}-{previous_month:02d}", f"{previous_year}-{previous_month:02d}"),
        "previous_key": f"{previous_year}-{previous_month:02d}",
        "current_label": month,
        "previous_label": f"{previous_year}-{previous_month:02d}",
    }


def _comparison(cur, scope, raw_period, raw_against, lang, mode="free", filters=None):
    comparison_period = _comparison_period(scope, raw_period, lang)
    if mode == "yoy":
        if scope == "year":
            raw_against = str(int(comparison_period["key"]) - 1)
        elif scope == "quarter":
            year, quarter = comparison_period["key"].split("-")
            raw_against = f"{int(year) - 1}-{quarter}"
        else:
            year, month = comparison_period["key"].split("-")
            raw_against = f"{int(year) - 1}-{month}"
    elif mode == "mom":
        raw_against = None
    against_period = _comparison_period(scope, raw_against, lang) if raw_against else None
    against_range = against_period["current"] if against_period else comparison_period["previous"]
    comparison_period["against_range"] = against_range
    comparison_period["against_key"] = (
        against_period["key"] if against_period else comparison_period["previous_key"]
    )
    comparison_period["against_label"] = (
        against_period["current_label"] if against_period else comparison_period["previous_label"]
    )
    current = _summary_between(cur, *comparison_period["current"], filters)
    previous = _summary_between(cur, *against_range, filters)
    metrics = []
    for key in ("income", "expense", "saving", "balance"):
        difference = current[key] - previous[key]
        percentage = None if previous[key] == 0 else float((difference / abs(previous[key])) * 100)
        favorable = difference <= 0 if key == "expense" else difference >= 0
        metrics.append({
            "key": key,
            "current": current[key],
            "previous": previous[key],
            "difference": difference,
            "percentage": percentage,
            "favorable": favorable,
        })
    return comparison_period, metrics


def _category_comparison(cur, comparison_period, lang, filters=None):
    def totals(date_range):
        filter_sql, filter_params = _filter_sql(filters)
        cur.execute(
            f"""
            SELECT COALESCE(c.name, 'Uncategorized'), SUM(r.amount)
            FROM records r
            LEFT JOIN categories c ON c.id=r.category_id
            WHERE r.type='expense' AND r.source='monthly'
              AND r.date >= %s AND r.date <= %s
              {filter_sql}
            GROUP BY COALESCE(c.name, 'Uncategorized')
            """,
            (*date_range, *filter_params),
        )
        return {row[0]: Decimal(row[1] or 0) for row in cur.fetchall()}

    current = totals(comparison_period["current"])
    previous = totals(comparison_period["against_range"])
    rows = []
    for name in current.keys() | previous.keys():
        label = ("Sin categoría" if lang == "es" else "Uncategorized") if name == "Uncategorized" else category_name(name, lang)
        current_amount = current.get(name, Decimal("0"))
        previous_amount = previous.get(name, Decimal("0"))
        difference = current_amount - previous_amount
        percentage = None if previous_amount == 0 else float((difference / previous_amount) * 100)
        status = "new" if previous_amount == 0 and current_amount > 0 else (
            "stopped" if current_amount == 0 and previous_amount > 0 else "comparable"
        )
        rows.append({
            "name": label,
            "current": current_amount,
            "previous": previous_amount,
            "difference": difference,
            "percentage": percentage,
            "status": status,
        })
    rows.sort(key=lambda row: abs(row["difference"]), reverse=True)
    increases = sorted((row for row in rows if row["difference"] > 0), key=lambda row: row["difference"], reverse=True)[:5]
    decreases = sorted((row for row in rows if row["difference"] < 0), key=lambda row: row["difference"])[:5]
    return rows, increases, decreases


def _comparison_options(cur, scope, lang, selected_keys):
    cur.execute("SELECT COALESCE(value, 1) FROM settings WHERE key='records_years'")
    row = cur.fetchone()
    years_count = min(max(int(row[0] if row else 1), 1), 10)
    now = datetime.now()
    years = range(now.year, now.year - years_count, -1)
    month_names = (
        ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        if lang == "es"
        else ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    )
    options = []
    if scope == "year":
        options = [{"value": str(year), "label": str(year)} for year in years]
    elif scope == "quarter":
        current_quarter = ((now.month - 1) // 3) + 1
        prefix = "T" if lang == "es" else "Q"
        options = [
            {"value": f"{year}-Q{quarter}", "label": f"{year} {prefix}{quarter}"}
            for year in years
            for quarter in range(4, 0, -1)
            if year < now.year or quarter <= current_quarter
        ]
    else:
        options = [
            {"value": f"{year}-{month:02d}", "label": f"{month_names[month - 1]} {year}"}
            for year in years
            for month in range(12, 0, -1)
            if year < now.year or month <= now.month
        ]
    existing = {option["value"] for option in options}
    for key in selected_keys:
        if key not in existing:
            options.append({"value": key, "label": key})
    return options


def _shift_month(year, month, offset):
    index = year * 12 + month - 1 + offset
    shifted_year, shifted_month = divmod(index, 12)
    return shifted_year, shifted_month + 1


def _evolution_data(cur, evolution_range, lang, filters=None):
    now = datetime.now()
    if evolution_range == "years":
        cur.execute("SELECT COALESCE(value, 1) FROM settings WHERE key='records_years'")
        row = cur.fetchone()
        years_count = min(max(int(row[0] if row else 1), 1), 10)
        keys = [str(year) for year in range(now.year - years_count + 1, now.year + 1)]
        key_expression = "SUBSTRING(r.date, 1, 4)"
        params = (f"{keys[0]}-01", f"{keys[-1]}-12")
    else:
        months_count = 6 if evolution_range == "6m" else 12
        keys = [
            f"{year}-{month:02d}"
            for year, month in (
                _shift_month(now.year, now.month, offset)
                for offset in range(-(months_count - 1), 1)
            )
        ]
        key_expression = "r.date"
        params = (keys[0], keys[-1])
    filter_sql, filter_params = _filter_sql(filters)
    cur.execute(
        f"""
        SELECT {key_expression},
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END), 0)
        FROM records r
        WHERE r.date >= %s AND r.date <= %s{filter_sql}
        GROUP BY {key_expression}
        ORDER BY {key_expression}
        """,
        (*params, *filter_params),
    )
    values = {
        row[0]: tuple(Decimal(value or 0) for value in row[1:])
        for row in cur.fetchall()
    }
    month_names = (
        ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        if lang == "es"
        else ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    )
    result = []
    for key in keys:
        income, expense, saving = values.get(key, (Decimal("0"),) * 3)
        label = key if evolution_range == "years" else f"{month_names[int(key[5:7]) - 1]} {key[:4]}"
        result.append({
            "key": key,
            "label": label,
            "income": float(income),
            "expense": float(expense),
            "saving": float(saving),
            "balance": float(income - expense - saving),
        })
    return result


def _category_summary(cur, report_type, period, lang, filters=None):
    if report_type == "yearly":
        where = "r.date >= %s AND r.date <= %s"
        params = (f"{period}-01", f"{period}-12")
    else:
        where = "r.date=%s"
        params = (period,)
    filter_sql, filter_params = _filter_sql(filters)
    cur.execute(
        f"""
        SELECT COALESCE(c.name, 'Uncategorized'), SUM(r.amount)
        FROM records r
        LEFT JOIN categories c ON c.id=r.category_id
        WHERE r.type='expense' AND r.source='monthly' AND {where}{filter_sql}
        GROUP BY COALESCE(c.name, 'Uncategorized')
        ORDER BY SUM(r.amount) DESC
        """,
        params + tuple(filter_params),
    )
    rows = cur.fetchall()
    result = []
    for name, amount in rows:
        label = "Sin categoría" if lang == "es" and name == "Uncategorized" else name
        if name != "Uncategorized":
            label = category_name(name, lang)
        result.append({"name": label, "amount": Decimal(amount or 0)})
    return result


def _top_expenses(cur, report_type, period, filters=None):
    if report_type == "yearly":
        where = "date >= %s AND date <= %s"
        params = (f"{period}-01", f"{period}-12")
    else:
        where = "date=%s"
        params = (period,)
    filter_sql, filter_params = _filter_sql(filters)
    cur.execute(
        f"""
        SELECT concept, SUM(amount)
        FROM records r
        WHERE type='expense' AND source='monthly' AND {where}{filter_sql}
        GROUP BY concept
        ORDER BY SUM(amount) DESC
        LIMIT 15
        """,
        params + tuple(filter_params),
    )
    return [{"concept": row[0], "amount": Decimal(row[1] or 0)} for row in cur.fetchall()]


@reports_bp.route("/reports/template-preview")
def template_preview():
    report_type = (request.args.get("type") or "monthly").strip().lower()
    if report_type not in {"monthly", "yearly"}:
        report_type = "monthly"
    period = _valid_period(report_type, request.args.get("period"))
    version = _normalize_version(request.args.get("version"))
    lang = session.get("lang") or "en"
    texts = _report_texts(lang)

    with get_db() as conn:
        with conn.cursor() as cur:
            summary = _summary(cur, report_type, period)
            categories = _category_summary(cur, report_type, period, lang)
            top_expenses = _top_expenses(cur, report_type, period)

    html = render_report_html(
        template_version=version,
        title=texts["title_yearly" if report_type == "yearly" else "title_monthly"],
        period_label=period,
        income=summary["income"],
        expense=summary["expense"],
        saving=summary["saving"],
        balance=summary["balance"],
        top_expenses=[(item["concept"], item["amount"]) for item in top_expenses],
        category_summary=[(item["name"], item["amount"]) for item in categories],
        texts=texts,
        include_top_expenses=report_type == "monthly",
        lang=lang,
    )
    return Response(html, mimetype="text/html")


@reports_bp.route("/reports/export.csv")
def export_csv():
    section = (request.args.get("section") or "summary").strip().lower()
    filters = _report_filters(request.args)
    lang = session.get("lang") or "en"
    output = io.StringIO()
    writer = csv.writer(output)

    with get_db() as conn:
        with conn.cursor() as cur:
            if section == "evolution":
                evolution_range = (request.args.get("evolution_range") or "6m").strip().lower()
                if evolution_range not in {"6m", "12m", "years"}:
                    evolution_range = "6m"
                rows = _evolution_data(cur, evolution_range, lang, filters)
                writer.writerow(["period", "income", "expense", "saving", "balance"])
                for row in rows:
                    writer.writerow([row["key"], row["income"], row["expense"], row["saving"], row["balance"]])
                filename = f"finance-evolution-{evolution_range}.csv"
            elif section == "comparisons":
                kinds = {
                    "free_month": ("free", "month"), "free_quarter": ("free", "quarter"),
                    "free_year": ("free", "year"), "mom": ("mom", "month"),
                    "yoy_month": ("yoy", "month"), "yoy_quarter": ("yoy", "quarter"),
                    "yoy_year": ("yoy", "year"),
                }
                mode, scope = kinds.get(request.args.get("comparison_kind"), ("free", "month"))
                comparison_period, metrics = _comparison(
                    cur, scope, request.args.get("comparison_period"),
                    request.args.get("comparison_against"), lang, mode, filters,
                )
                category_rows, _, _ = _category_comparison(cur, comparison_period, lang, filters)
                writer.writerow(["metric", "current", "comparison", "difference", "percentage"])
                for metric in metrics:
                    writer.writerow([
                        metric["key"], metric["current"], metric["previous"],
                        metric["difference"], metric["percentage"],
                    ])
                writer.writerow([])
                writer.writerow(["category", "current", "comparison", "difference", "percentage", "status"])
                for row in category_rows:
                    writer.writerow([
                        row["name"], row["current"], row["previous"], row["difference"],
                        row["percentage"], row["status"],
                    ])
                filename = f"finance-comparison-{comparison_period['key']}.csv"
            else:
                report_type = (request.args.get("type") or "monthly").strip().lower()
                report_type = report_type if report_type in {"monthly", "yearly"} else "monthly"
                period = _valid_period(report_type, request.args.get("period"))
                summary = _summary(cur, report_type, period, filters)
                categories = _category_summary(cur, report_type, period, lang, filters)
                writer.writerow(["metric", "amount"])
                for key in ("income", "expense", "saving", "balance"):
                    writer.writerow([key, summary[key]])
                writer.writerow([])
                writer.writerow(["category", "expense"])
                for row in categories:
                    writer.writerow([row["name"], row["amount"]])
                filename = f"finance-summary-{period}.csv"

    response = Response("\ufeff" + output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@reports_bp.route("/reports/print")
def print_report():
    section = (request.args.get("section") or "summary").strip().lower()
    filters = _report_filters(request.args)
    lang = session.get("lang") or "en"
    payload = {"section": section, "generated_at": datetime.now(), "filters": []}
    with get_db() as conn:
        with conn.cursor() as cur:
            if filters["category_id"]:
                cur.execute("SELECT name FROM categories WHERE id=%s", (filters["category_id"],))
                row = cur.fetchone()
                if row:
                    payload["filters"].append(category_name(row[0], lang))
            if filters["bank_id"]:
                cur.execute("SELECT name FROM banks WHERE id=%s", (filters["bank_id"],))
                row = cur.fetchone()
                if row:
                    payload["filters"].append(row[0])
            if section == "evolution":
                evolution_range = (request.args.get("evolution_range") or "6m").strip().lower()
                evolution_range = evolution_range if evolution_range in {"6m", "12m", "years"} else "6m"
                payload.update({"range": evolution_range, "evolution": _evolution_data(cur, evolution_range, lang, filters)})
            elif section == "comparisons":
                kinds = {
                    "free_month": ("free", "month"), "free_quarter": ("free", "quarter"),
                    "free_year": ("free", "year"), "mom": ("mom", "month"),
                    "yoy_month": ("yoy", "month"), "yoy_quarter": ("yoy", "quarter"),
                    "yoy_year": ("yoy", "year"),
                }
                mode, scope = kinds.get(request.args.get("comparison_kind"), ("free", "month"))
                comparison_period, metrics = _comparison(
                    cur, scope, request.args.get("comparison_period"),
                    request.args.get("comparison_against"), lang, mode, filters,
                )
                categories, _, _ = _category_comparison(cur, comparison_period, lang, filters)
                payload.update({"period": comparison_period, "metrics": metrics, "categories": categories})
            else:
                payload["section"] = "summary"
                report_type = (request.args.get("type") or "monthly").strip().lower()
                report_type = report_type if report_type in {"monthly", "yearly"} else "monthly"
                period = _valid_period(report_type, request.args.get("period"))
                payload.update({
                    "period_label": period,
                    "summary": _summary(cur, report_type, period, filters),
                    "categories": _category_summary(cur, report_type, period, lang, filters),
                })
    return render_template("report_print.html", report=payload)


@reports_bp.route("/reports/saved/save", methods=["POST"])
def save_report():
    name = (request.form.get("name") or "").strip()[:80]
    section = (request.form.get("section") or "summary").strip().lower()
    query_string = (request.form.get("query_string") or "").strip()[:2000]
    if name and section in {"summary", "comparisons", "evolution"}:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO saved_reports (user_id, name, section, query_string)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (session["user_id"], name, section, query_string),
                )
                conn.commit()
        session["reports_msg"] = "Informe guardado." if session.get("lang") == "es" else "Report saved."
    return redirect(url_for("reports.reports", section="saved"))


@reports_bp.route("/reports/saved/<int:report_id>/delete", methods=["POST"])
def delete_saved_report(report_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM saved_reports WHERE id=%s AND user_id=%s",
                (report_id, session["user_id"]),
            )
            conn.commit()
    session["reports_msg"] = "Informe eliminado." if session.get("lang") == "es" else "Report deleted."
    return redirect(url_for("reports.reports", section="saved"))


@reports_bp.route("/reports")
def reports():
    section = (request.args.get("section") or "summary").strip().lower()
    if section not in {"summary", "comparisons", "evolution", "saved", "delivery", "templates"}:
        section = "summary"
    report_type = (request.args.get("type") or "monthly").strip().lower()
    if report_type not in {"monthly", "yearly"}:
        report_type = "monthly"
    period = _valid_period(report_type, request.args.get("period"))
    lang = session.get("lang") or "en"
    filters = _report_filters(request.args)
    comparison_kinds = {
        "free_month": ("free", "month"),
        "free_quarter": ("free", "quarter"),
        "free_year": ("free", "year"),
        "mom": ("mom", "month"),
        "yoy_month": ("yoy", "month"),
        "yoy_quarter": ("yoy", "quarter"),
        "yoy_year": ("yoy", "year"),
    }
    requested_kind = (request.args.get("comparison_kind") or "").strip().lower()
    if requested_kind in comparison_kinds:
        comparison_kind = requested_kind
        comparison_mode, comparison_scope = comparison_kinds[requested_kind]
    else:
        comparison_scope = (request.args.get("comparison_scope") or "month").strip().lower()
        if comparison_scope not in {"month", "quarter", "year"}:
            comparison_scope = "month"
        comparison_mode = (request.args.get("comparison_mode") or "free").strip().lower()
        if comparison_mode not in {"free", "mom", "yoy"}:
            comparison_mode = "free"
        if comparison_mode == "mom":
            comparison_scope = "month"
        comparison_kind = (
            "mom" if comparison_mode == "mom"
            else f"{comparison_mode}_{comparison_scope}"
        )
    evolution_range = (request.args.get("evolution_range") or "6m").strip().lower()
    if evolution_range not in {"6m", "12m", "years"}:
        evolution_range = "6m"

    with get_db() as conn:
        with conn.cursor() as cur:
            summary = _summary(cur, report_type, period, filters)
            categories = _category_summary(cur, report_type, period, lang, filters)
            top_expenses = _top_expenses(cur, report_type, period, filters)
            config = _report_config(cur)
            cur.execute(
                """
                SELECT report_type, period_key, status, message, created_at
                FROM email_report_runs
                ORDER BY created_at DESC, id DESC
                LIMIT 10
                """
            )
            runs = cur.fetchall()
            comparison_period, comparison_metrics = _comparison(
                cur,
                comparison_scope,
                request.args.get("comparison_period"),
                request.args.get("comparison_against"),
                lang,
                comparison_mode,
                filters,
            )
            category_comparison, category_increases, category_decreases = _category_comparison(
                cur, comparison_period, lang, filters
            )
            comparison_options = _comparison_options(
                cur,
                comparison_scope,
                lang,
                (comparison_period["key"], comparison_period["against_key"]),
            )
            evolution_data = _evolution_data(cur, evolution_range, lang, filters)
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            filter_categories = [
                (row[0], category_name(row[1], lang)) for row in cur.fetchall()
            ]
            cur.execute("SELECT id, name FROM banks ORDER BY name")
            filter_banks = cur.fetchall()
            cur.execute(
                "SELECT id, name, bank_id FROM payment_methods WHERE kind='bank_account' ORDER BY name"
            )
            filter_accounts = cur.fetchall()
            cur.execute(
                "SELECT id, name, bank_id FROM payment_methods WHERE kind='card' ORDER BY name"
            )
            filter_cards = cur.fetchall()
            cur.execute("SELECT id, name, bank_id FROM loans ORDER BY name")
            filter_loans = cur.fetchall()
            cur.execute(
                """
                SELECT id, name, section, query_string, created_at
                FROM saved_reports
                WHERE user_id=%s
                ORDER BY created_at DESC, id DESC
                """,
                (session["user_id"],),
            )
            saved_reports = cur.fetchall()

    max_category_amount = max((item["amount"] for item in categories), default=Decimal("0"))
    for item in categories:
        item["percentage"] = (
            float((item["amount"] / max_category_amount) * 100)
            if max_category_amount > 0
            else 0
        )

    message = session.pop("reports_msg", None)
    error = session.pop("reports_err", None)
    return render_template(
        "reports.html",
        report_type=report_type,
        reports_section=section,
        period=period,
        current_year=datetime.now().year,
        comparison_scope=comparison_scope,
        comparison_mode=comparison_mode,
        comparison_kind=comparison_kind,
        comparison_period=comparison_period,
        comparison_metrics=comparison_metrics,
        category_comparison=category_comparison,
        category_increases=category_increases,
        category_decreases=category_decreases,
        comparison_options=comparison_options,
        evolution_range=evolution_range,
        evolution_data=evolution_data,
        report_filters=filters,
        filter_categories=filter_categories,
        filter_banks=filter_banks,
        filter_accounts=filter_accounts,
        filter_cards=filter_cards,
        filter_loans=filter_loans,
        saved_reports=saved_reports,
        current_query=request.query_string.decode("utf-8"),
        summary=summary,
        categories=categories,
        top_expenses=top_expenses,
        report_cfg=config,
        runs=runs,
        message=message,
        error=error,
        can_configure=session.get("role") in {"admin", "editor"},
        current_page="reports",
    )
