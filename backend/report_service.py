import logging
import os
import threading
import time
from datetime import datetime

from db import get_db
from email_service import send_email
from i18n import category_name, format_money
from report_templates import render_report_html


logger = logging.getLogger("finance.reports")
_THREAD = None
_THREAD_LOCK = threading.Lock()
_STOP_EVENT = threading.Event()
_SLEEP_SECONDS = 60


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _public_url() -> str:
    return (os.environ.get("APP_PUBLIC_URL") or "").strip().rstrip("/")


def _prev_month(ref: datetime) -> datetime:
    year = ref.year
    month = ref.month - 1
    if month == 0:
        month = 12
        year -= 1
    return ref.replace(year=year, month=month, day=1)


def _prev_year_key(ref: datetime) -> str:
    return str(ref.year - 1)


def _load_config(cur):
    cur.execute(
        """
        SELECT monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version
        FROM email_report_config
        WHERE id=1
        """
    )
    row = cur.fetchone()
    if not row:
        cur.execute(
            """
            INSERT INTO email_report_config (
                id, monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version, updated_at
            )
            VALUES (1, TRUE, TRUE, 'v1', 'v1', NOW())
            """
        )
        return {
            "monthly_enabled": True,
            "yearly_enabled": True,
            "monthly_template_version": "v1",
            "yearly_template_version": "v1",
        }
    return {
        "monthly_enabled": bool(row[0]),
        "yearly_enabled": bool(row[1]),
        "monthly_template_version": _normalize_template_version(row[2]),
        "yearly_template_version": _normalize_template_version(row[3]),
    }


def _normalize_lang(lang: str | None) -> str:
    value = (lang or "en").strip().lower()
    return "es" if value == "es" else "en"


def _normalize_template_version(value: str | None) -> str:
    return "v1" if (value or "").strip().lower() != "v1" else "v1"


def _report_texts(lang: str) -> dict:
    lang = _normalize_lang(lang)
    if lang == "es":
        return {
            "subject_monthly": "Balance mensual de Finance - {period}",
            "subject_yearly": "Balance anual de Finance - {period}",
            "title_monthly": "Balance Mensual de Finance",
            "title_yearly": "Balance Anual de Finance",
            "period": "Periodo",
            "open_finance": "Abrir Finance",
            "summary_title": "Ingreso / Gasto / Ahorro",
            "income": "Ingreso",
            "expense": "Gasto",
            "saving": "Ahorro",
            "balance": "Balance",
            "category_summary": "Resumen de gastos por categoria",
            "top_expenses": "Top 15 gastos",
            "concept": "Concepto",
            "category": "Categoria",
            "amount": "Importe",
            "no_expense_data": "Sin datos de gastos.",
            "no_category_data": "Sin datos por categoria.",
            "finance_url": "URL de Finance",
            "open_finance_line": "Abrir Finance",
            "monthly_body_intro": "Balance mensual para {period}",
            "yearly_body_intro": "Balance anual para {period}",
            "uncategorized": "Sin categoria",
        }
    return {
        "subject_monthly": "Finance monthly balance - {period}",
        "subject_yearly": "Finance yearly balance - {period}",
        "title_monthly": "Finance Monthly Balance",
        "title_yearly": "Finance Yearly Balance",
        "period": "Period",
        "open_finance": "Open Finance",
        "summary_title": "Income / Expense / Saving",
        "income": "Income",
        "expense": "Expense",
        "saving": "Saving",
        "balance": "Balance",
        "category_summary": "Expense summary by category",
        "top_expenses": "Top 15 Expenses",
        "concept": "Concept",
        "category": "Category",
        "amount": "Amount",
        "no_expense_data": "No expense data.",
        "no_category_data": "No category data.",
        "finance_url": "Finance URL",
        "open_finance_line": "Open Finance",
        "monthly_body_intro": "Monthly balance for {period}",
        "yearly_body_intro": "Yearly balance for {period}",
        "uncategorized": "Uncategorized",
    }


def _active_recipients(cur):
    cur.execute(
        """
        SELECT email, COALESCE(language, 'en')
        FROM users
        WHERE is_active=TRUE AND COALESCE(email_notifications, TRUE)=TRUE
        """
    )
    return [(r[0], _normalize_lang(r[1])) for r in cur.fetchall() if r and r[0]]


def _resolve_recipient_languages(cur, recipients_override=None):
    if not recipients_override:
        return _active_recipients(cur)

    requested = []
    seen = set()
    for raw in recipients_override:
        email = (raw or "").strip()
        if not email:
            continue
        key = email.lower()
        if key in seen:
            continue
        seen.add(key)
        requested.append(email)
    if not requested:
        return []

    cur.execute(
        """
        SELECT LOWER(email), COALESCE(language, 'en')
        FROM users
        WHERE LOWER(email) = ANY(%s)
        """,
        ([e.lower() for e in requested],),
    )
    by_email = {row[0]: _normalize_lang(row[1]) for row in cur.fetchall() if row and row[0]}
    return [(email, by_email.get(email.lower(), "en")) for email in requested]


def _already_sent(cur, report_type: str, period_key: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM email_report_runs
        WHERE report_type=%s AND period_key=%s AND status='success'
        LIMIT 1
        """,
        (report_type, period_key),
    )
    return bool(cur.fetchone())


def _record_run(cur, report_type: str, period_key: str, status: str, message: str | None):
    cur.execute(
        """
        INSERT INTO email_report_runs (report_type, period_key, status, message, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        """,
        (report_type, period_key, status, (message or "")[:1000]),
    )


def _monthly_payload(cur, period_key: str):
    cur.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN type='expense' AND source='monthly' THEN amount ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END),0)
        FROM records
        WHERE date=%s
        """,
        (period_key,),
    )
    income, expense, saving = cur.fetchone()
    balance = income - expense - saving
    return income, expense, saving, balance


def _yearly_payload(cur, year_key: str):
    cur.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN type='saving' THEN amount ELSE 0 END),0)
        FROM records
        WHERE date >= %s AND date <= %s
        """,
        (f"{year_key}-01", f"{year_key}-12"),
    )
    income, expense, saving = cur.fetchone()
    balance = income - expense - saving
    return income, expense, saving, balance


def _monthly_top_expenses(cur, period_key: str):
    cur.execute(
        """
        SELECT concept, SUM(amount) AS total_amount
        FROM records
        WHERE type='expense' AND source='monthly' AND date=%s
        GROUP BY concept
        ORDER BY total_amount DESC
        LIMIT 15
        """,
        (period_key,),
    )
    return cur.fetchall()


def _yearly_top_expenses(cur, year_key: str):
    cur.execute(
        """
        SELECT concept, SUM(amount) AS total_amount
        FROM records
        WHERE type='expense'
          AND date >= %s
          AND date <= %s
        GROUP BY concept
        ORDER BY total_amount DESC
        LIMIT 15
        """,
        (f"{year_key}-01", f"{year_key}-12"),
    )
    return cur.fetchall()


def _monthly_category_summary(cur, period_key: str):
    cur.execute(
        """
        SELECT COALESCE(c.name, 'Uncategorized') AS category_name, SUM(r.amount) AS total_amount
        FROM records r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.type='expense' AND r.source='monthly' AND r.date=%s
        GROUP BY COALESCE(c.name, 'Uncategorized')
        ORDER BY total_amount DESC
        """,
        (period_key,),
    )
    return cur.fetchall()


def _yearly_category_summary(cur, year_key: str):
    cur.execute(
        """
        SELECT COALESCE(c.name, 'Uncategorized') AS category_name, SUM(r.amount) AS total_amount
        FROM records r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.type='expense'
          AND r.date >= %s
          AND r.date <= %s
        GROUP BY COALESCE(c.name, 'Uncategorized')
        ORDER BY total_amount DESC
        """,
        (f"{year_key}-01", f"{year_key}-12"),
    )
    return cur.fetchall()


def _render_report_html(template_version="v1", **kwargs):
    return render_report_html(template_version=template_version, **kwargs)


def send_monthly_report(test=False, recipients_override=None):
    now = datetime.now()
    period_key = _month_key(now) if test else _month_key(_prev_month(now))
    report_type = "test_monthly" if test else "monthly"

    with get_db() as conn:
        with conn.cursor() as cur:
            config = _load_config(cur)
            if not test and _already_sent(cur, "monthly", period_key):
                return True, "already_sent"

            recipients = _resolve_recipient_languages(cur, recipients_override)
            if not recipients and not test:
                _record_run(cur, report_type, period_key, "failed", "No active recipients")
                conn.commit()
                return False, "No active recipients"

            income, expense, saving, balance = _monthly_payload(cur, period_key)
            top_expenses = _monthly_top_expenses(cur, period_key)
            category_summary = _monthly_category_summary(cur, period_key)
            if test and not recipients:
                _record_run(cur, report_type, period_key, "failed", "No test recipient")
                conn.commit()
                return False, "No test recipient"

            by_lang = {}
            for email, lang in recipients:
                by_lang.setdefault(_normalize_lang(lang), []).append(email)

            all_ok = True
            for lang, lang_recipients in by_lang.items():
                texts = _report_texts(lang)
                localized_categories = []
                for name, total_amount in category_summary:
                    if (name or "") == "Uncategorized":
                        label = texts["uncategorized"]
                    else:
                        label = category_name(name or "", lang)
                    localized_categories.append((label, total_amount))

                subject = texts["subject_monthly"].format(period=period_key)
                body = (
                    f"{texts['monthly_body_intro'].format(period=period_key)}\n\n"
                    f"{texts['income']}: {format_money(income, lang)}\n"
                    f"{texts['expense']}: {format_money(expense, lang)}\n"
                    f"{texts['saving']}: {format_money(saving, lang)}\n"
                    f"{texts['balance']}: {format_money(balance, lang)}\n"
                )
                if _public_url():
                    body += f"\n{texts['open_finance_line']}: {_public_url()}\n"
                html_body = _render_report_html(
                    template_version=config["monthly_template_version"],
                    title=texts["title_monthly"],
                    period_label=period_key,
                    income=income,
                    expense=expense,
                    saving=saving,
                    balance=balance,
                    top_expenses=top_expenses,
                    category_summary=localized_categories,
                    texts=texts,
                    include_top_expenses=True,
                    lang=lang,
                )
                ok = send_email(lang_recipients, subject, body, html_body=html_body)
                all_ok = all_ok and ok

            _record_run(cur, report_type, period_key, "success" if all_ok else "failed", "sent" if all_ok else "send failed")
            conn.commit()
            return (all_ok, "sent" if all_ok else "send failed")


def send_yearly_report(test=False, recipients_override=None):
    now = datetime.now()
    period_key = _prev_year_key(now)
    report_type = "test_yearly" if test else "yearly"

    with get_db() as conn:
        with conn.cursor() as cur:
            config = _load_config(cur)
            if not test and _already_sent(cur, "yearly", period_key):
                return True, "already_sent"

            recipients = _resolve_recipient_languages(cur, recipients_override)
            if not recipients and not test:
                _record_run(cur, report_type, period_key, "failed", "No active recipients")
                conn.commit()
                return False, "No active recipients"

            income, expense, saving, balance = _yearly_payload(cur, period_key)
            category_summary = _yearly_category_summary(cur, period_key)
            if test and not recipients:
                _record_run(cur, report_type, period_key, "failed", "No test recipient")
                conn.commit()
                return False, "No test recipient"

            by_lang = {}
            for email, lang in recipients:
                by_lang.setdefault(_normalize_lang(lang), []).append(email)

            all_ok = True
            for lang, lang_recipients in by_lang.items():
                texts = _report_texts(lang)
                localized_categories = []
                for name, total_amount in category_summary:
                    if (name or "") == "Uncategorized":
                        label = texts["uncategorized"]
                    else:
                        label = category_name(name or "", lang)
                    localized_categories.append((label, total_amount))

                subject = texts["subject_yearly"].format(period=period_key)
                body = (
                    f"{texts['yearly_body_intro'].format(period=period_key)}\n\n"
                    f"{texts['income']}: {format_money(income, lang)}\n"
                    f"{texts['expense']}: {format_money(expense, lang)}\n"
                    f"{texts['saving']}: {format_money(saving, lang)}\n"
                    f"{texts['balance']}: {format_money(balance, lang)}\n"
                )
                if _public_url():
                    body += f"\n{texts['open_finance_line']}: {_public_url()}\n"
                html_body = _render_report_html(
                    template_version=config["yearly_template_version"],
                    title=texts["title_yearly"],
                    period_label=period_key,
                    income=income,
                    expense=expense,
                    saving=saving,
                    balance=balance,
                    top_expenses=[],
                    category_summary=localized_categories,
                    texts=texts,
                    include_top_expenses=False,
                    lang=lang,
                )
                ok = send_email(lang_recipients, subject, body, html_body=html_body)
                all_ok = all_ok and ok

            _record_run(cur, report_type, period_key, "success" if all_ok else "failed", "sent" if all_ok else "send failed")
            conn.commit()
            return (all_ok, "sent" if all_ok else "send failed")


def maybe_run_scheduled_reports():
    now = datetime.now()
    if now.day != 1:
        return
    # Simple cron style: first minute window after midnight.
    if now.hour != 0:
        return

    with get_db() as conn:
        with conn.cursor() as cur:
            config = _load_config(cur)
            conn.commit()

    if config["monthly_enabled"]:
        ok, msg = send_monthly_report(test=False)
        logger.info("monthly_report_run ok=%s msg=%s", ok, msg)
    if config["yearly_enabled"] and now.month == 1:
        ok, msg = send_yearly_report(test=False)
        logger.info("yearly_report_run ok=%s msg=%s", ok, msg)


def _worker_loop():
    logger.info("report_scheduler_started")
    while not _STOP_EVENT.is_set():
        try:
            maybe_run_scheduled_reports()
        except Exception as exc:  # pragma: no cover
            logger.warning("report_scheduler_error error=%s", exc)
        _STOP_EVENT.wait(_SLEEP_SECONDS)


def start_report_scheduler():
    global _THREAD
    with _THREAD_LOCK:
        if _THREAD and _THREAD.is_alive():
            return
        _STOP_EVENT.clear()
        _THREAD = threading.Thread(target=_worker_loop, daemon=True, name="finance-report-scheduler")
        _THREAD.start()
