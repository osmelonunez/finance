import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import pytest
from psycopg2 import sql
from werkzeug.security import generate_password_hash


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TESTS = ROOT / "tests"
for path in (BACKEND, TESTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from endpoint_reporting import write_catalog, write_execution_report

os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("FINANCE_DISABLE_SCHEDULERS", "true")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")
os.environ.setdefault("SECRET_KEY", "finance-test-secret")
os.environ.setdefault("SMTP_ENCRYPTION_KEY", "finance-test-smtp-key")
os.environ.setdefault("DB_CONFIG_ENCRYPTION_KEY", "finance-test-db-key")

ROUTE_RESULTS = {}
TEST_OUTCOMES = {}
ROUTE_CHECKS = {
    "test_every_endpoint_method_responds_without_server_error": "contract",
    "test_every_mutating_endpoint_rejects_missing_csrf": "csrf",
    "test_every_private_endpoint_requires_authentication": "auth",
}


def _test_database_url():
    if (os.environ.get("APP_ENV") or "").strip().lower() != "testing":
        raise RuntimeError("Tests refuse to run unless APP_ENV=testing.")
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    database_name = urlparse(database_url).path.lstrip("/")
    if not database_url or not database_name.endswith("_test"):
        raise RuntimeError("Tests refuse to run unless DATABASE_URL points to a database ending in '_test'.")
    return database_url


def _reset_and_seed_database():
    database_url = _test_database_url()
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            current_database = cur.fetchone()[0]
            if not current_database.endswith("_test"):
                raise RuntimeError("Refusing to reset a non-test database.")

            cur.execute(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname='public' AND tablename <> 'migrations'
                """
            )
            tables = [row[0] for row in cur.fetchall()]
            if tables:
                cur.execute(
                    sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(
                        sql.SQL(", ").join(sql.Identifier(table) for table in tables)
                    )
                )

            password_hash = generate_password_hash("FinanceTest1")
            cur.execute(
                """
                INSERT INTO users (id, email, username, password_hash, role, is_admin, is_active, language, per_page)
                VALUES
                    (1, 'admin@example.test', 'admin_test', %s, 'admin', TRUE, TRUE, 'es', 15),
                    (2, 'editor@example.test', 'editor_test', %s, 'editor', FALSE, TRUE, 'en', 15),
                    (3, 'user@example.test', 'user_test', %s, 'user', FALSE, TRUE, 'en', 15),
                    (4, 'pending@example.test', 'pending_test', %s, 'user', FALSE, FALSE, 'en', 15)
                """,
                (password_hash, password_hash, password_hash, password_hash),
            )
            cur.execute(
                """
                INSERT INTO settings (key, value)
                VALUES
                    ('app_initialized', 1),
                    ('initial_saving', 1000),
                    ('per_page', 15),
                    ('records_years', 3)
                """
            )
            cur.execute(
                """
                INSERT INTO categories (id, name, description)
                VALUES
                    (1, 'Food', 'Food test category'),
                    (2, 'Transport', 'Transport test category'),
                    (3, 'Unused', 'Category without records')
                """
            )
            cur.execute(
                """
                INSERT INTO banks (id, name, is_active)
                VALUES
                    (1, 'Test Bank', TRUE),
                    (2, 'Inactive Bank', FALSE),
                    (3, 'Empty Bank', TRUE)
                """
            )
            cur.execute(
                """
                INSERT INTO payment_methods (id, name, kind, bank_name, bank_id, account_ref, is_active)
                VALUES
                    (1, 'Test Card', 'card', 'Test Bank', 1, 'CARD-001', TRUE),
                    (2, 'Test Account', 'bank_account', 'Test Bank', 1, 'ACC-001', TRUE),
                    (3, 'Inactive Card', 'card', 'Inactive Bank', 2, 'CARD-002', FALSE),
                    (4, 'Unused Card', 'card', 'Test Bank', 1, 'CARD-004', TRUE)
                """
            )
            cur.execute(
                """
                INSERT INTO loans (
                    id, name, bank_name, bank_id, principal_amount, term_months,
                    monthly_payment, start_date, status, loan_type, total_repayment_amount,
                    created_by
                )
                VALUES
                    (1, 'Test Loan', 'Test Bank', 1, 10000, 24, 500, '2026-01', 'active', 'interest', 12000, 'admin_test'),
                    (2, 'Unused Loan', 'Test Bank', 1, 1000, 10, 100, '2026-01', 'active', 'standard', NULL, 'admin_test')
                """
            )
            cur.execute(
                """
                INSERT INTO loan_usages (id, loan_id, concept, amount, date, category_id, comment, created_by)
                VALUES (1, 1, 'Test usage', 75, '2026-07', 1, 'Usage fixture', 'admin_test')
                """
            )
            cur.execute(
                """
                INSERT INTO records (
                    id, concept, amount, date, type, source, comment, category_id,
                    payment_method_id, loan_id, is_loan_payment, created_by
                )
                VALUES
                    (1, 'Test expense', 1234.56, '2026-07', 'expense', 'monthly', 'Expense fixture', 1, 1, NULL, FALSE, 'admin_test'),
                    (2, 'Test income', 2500, '2026-07', 'income', NULL, 'Income fixture', 2, NULL, NULL, FALSE, 'admin_test'),
                    (3, 'Test saving', 500, '2026-07', 'saving', NULL, 'Saving fixture', 2, NULL, NULL, FALSE, 'admin_test'),
                    (4, 'Test loan payment', 100, '2026-07', 'expense', 'monthly', 'Loan payment fixture', 1, 2, 1, TRUE, 'admin_test')
                """
            )
            cur.execute(
                """
                INSERT INTO backup_config (id, frequency, weekly_day, retain_count)
                VALUES (1, 'daily', 0, 7)
                """
            )
            cur.execute(
                """
                INSERT INTO backup_runs (id, trigger, filename, file_path, status, message, created_by)
                VALUES (1, 'manual', 'missing.sql', '/tmp/finance-test-backups/missing.sql', 'failed', 'Fixture', 'admin_test')
                """
            )
            cur.execute(
                """
                INSERT INTO smtp_settings (id, port, use_tls, enabled)
                VALUES (1, 587, TRUE, FALSE)
                """
            )
            cur.execute(
                """
                INSERT INTO email_report_config (
                    id, monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version
                )
                VALUES (1, TRUE, TRUE, 'v1', 'v1')
                """
            )

            for table in ("users", "categories", "banks", "payment_methods", "loans", "loan_usages", "records", "backup_runs"):
                cur.execute(
                    sql.SQL(
                        "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                        "COALESCE((SELECT MAX(id) FROM {}), 1), TRUE)"
                    ).format(sql.Identifier(table)),
                    (table,),
                )
        conn.commit()


@pytest.fixture(scope="session")
def application():
    _test_database_url()
    from db import init_db

    init_db()
    from app import app

    app.config.update(TESTING=True, RATELIMIT_ENABLED=False)
    return app


@pytest.fixture(autouse=True)
def clean_database(request):
    if request.node.get_closest_marker("unit"):
        yield
        return
    request.getfixturevalue("application")
    _reset_and_seed_database()
    yield


@pytest.fixture
def client(application):
    return application.test_client()


def _set_session(client, role):
    users = {
        "admin": (1, "admin@example.test", "admin_test", True),
        "editor": (2, "editor@example.test", "editor_test", False),
        "user": (3, "user@example.test", "user_test", False),
    }
    user_id, email, username, is_admin = users[role]
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["user_email"] = email
        session["user_name"] = username
        session["role"] = role
        session["is_admin"] = is_admin
        session["per_page"] = 15
        session["lang"] = "es" if role == "admin" else "en"
        session["email_notifications"] = True
        session["csrf_token"] = "test-csrf-token"


@pytest.fixture
def login_as():
    return _set_session


@pytest.fixture
def admin_client(client, login_as):
    login_as(client, "admin")
    return client


@pytest.fixture
def db_query():
    def query(statement, params=(), fetch="one"):
        with psycopg2.connect(_test_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(statement, params)
                if fetch == "all":
                    return cur.fetchall()
                if fetch == "none":
                    conn.commit()
                    return None
                return cur.fetchone()

    return query


def pytest_sessionstart(session):
    ROUTE_RESULTS.clear()
    TEST_OUTCOMES.clear()
    from app import app

    write_catalog(app)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" or (report.when in {"setup", "teardown"} and report.failed):
        status = "OK" if report.passed else ("OMITIDO" if report.skipped else "FALLO")
        if report.when == "call" or status == "FALLO":
            TEST_OUTCOMES[item.nodeid] = status

        check = ROUTE_CHECKS.get(getattr(item, "originalname", item.name))
        callspec = getattr(item, "callspec", None)
        if check and callspec:
            params = callspec.params
            key = (check, params["endpoint"], params["method"], params["path"])
            if report.when == "call" or status == "FALLO":
                ROUTE_RESULTS[key] = status


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    from app import app

    invocation = "pytest " + " ".join(str(arg) for arg in session.config.invocation_params.args)
    write_execution_report(app, ROUTE_RESULTS, TEST_OUTCOMES, session.exitstatus, invocation)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if config.option.markexpr == "unit":
        return
    from app import app

    rules = [rule for rule in app.url_map.iter_rules() if rule.endpoint != "static"]
    method_cases = sum(len(rule.methods - {"HEAD", "OPTIONS"}) for rule in rules)
    terminalreporter.write_sep(
        "=",
        f"Finance route inventory: {len(rules)} rules, {method_cases} endpoint-method combinations",
    )
