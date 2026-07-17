import re


CSRF_TOKEN = "test-csrf-token"
IGNORED_ENDPOINTS = {"static"}
PUBLIC_ENDPOINTS = {
    "health_live",
    "health_ready",
    "auth.login",
    "auth.register",
    "setup.setup_page",
    "setup.setup_use_existing",
    "setup.setup_create_new",
    "setup.setup_test_connection",
}

PATH_VALUES = {
    "id": "1",
    "method_id": "1",
    "bank_id": "1",
    "category_id": "1",
    "usage_id": "1",
    "run_id": "1",
    "user_id": "2",
    "section": "kpi",
    "filename": "style.css",
}

MOVEMENT_PAYLOAD = {
    "type": "expense",
    "from": "expense",
    "concept": "Release test expense",
    "amount": "25.50",
    "date": "2026-07",
    "source": "monthly",
    "category": "Food",
    "payment_method_id": "1",
    "comment": "Automated route test",
}

LOAN_PAYLOAD = {
    "name": "Release test loan",
    "bank_id": "1",
    "principal_amount": "1000",
    "term_months": "10",
    "monthly_payment": "100",
    "start_date": "2026-01",
    "status": "active",
    "loan_type": "standard",
    "description": "Automated route test",
}

POST_PAYLOADS = {
    "auth.login": {"email": "admin@example.test", "password": "FinanceTest1"},
    "auth.register": {
        "email": "new-user@example.test",
        "username": "new_user_test",
        "password": "FinanceTest1",
        "confirm": "FinanceTest1",
    },
    "auth.update_username": {"username": "admin_updated", "next": "/profile"},
    "auth.update_email": {"email": "admin-updated@example.test", "next": "/profile"},
    "auth.update_password": {
        "current_password": "FinanceTest1",
        "new_password": "FinanceTest2",
        "confirm_password": "FinanceTest2",
        "next": "/profile",
    },
    "auth.update_per_page_pref": {"per_page": "25", "next": "/profile"},
    "auth.update_language_pref": {"language": "es", "next": "/profile"},
    "auth.update_email_notifications_pref": {"email_notifications": "1", "next": "/profile"},
    "setup.setup_use_existing": {},
    "setup.setup_create_new": {},
    "setup.setup_test_connection": {},
    "categories.add_category": {"name": "Release Category", "description": "Automated route test"},
    "categories.update_category": {"name": "Food updated", "description": "Automated route test"},
    "categories.delete_category": {},
    "movements.add_movement": MOVEMENT_PAYLOAD,
    "movements.edit": MOVEMENT_PAYLOAD,
    "movements.duplicate": MOVEMENT_PAYLOAD,
    "movements.delete": {"from": "expense"},
    "movements.delete_all": {},
    "loans.loan_add": LOAN_PAYLOAD,
    "loans.loan_usage_add": {
        "concept": "Release usage",
        "amount": "10",
        "date": "2026-07",
        "category": "Food",
        "comment": "Automated route test",
    },
    "loans.loan_usage_update": {
        "concept": "Updated usage",
        "amount": "20",
        "date": "2026-07",
        "category": "Food",
        "comment": "Automated route test",
    },
    "loans.loan_usage_delete": {},
    "loans.loan_status": {"status": "active"},
    "loans.loan_details_update": LOAN_PAYLOAD,
    "loans.loan_dashboard_visibility": {"exclude_from_dashboard": "on"},
    "loans.loan_delete": {},
    "management.save_smtp": {"smtp_port": "587", "smtp_use_tls": "1"},
    "management.test_smtp": {},
    "management.save_email_reports": {
        "monthly_enabled": "1",
        "yearly_enabled": "1",
        "monthly_template_version": "v1",
        "yearly_template_version": "v1",
    },
    "management.test_monthly_report": {},
    "management.test_yearly_report": {},
    "management.add_payment_method": {
        "name": "Release Card",
        "kind": "card",
        "bank_id": "1",
        "account_ref": "REL-001",
        "is_active": "1",
    },
    "management.update_payment_method": {
        "name": "Test Card updated",
        "kind": "card",
        "bank_id": "1",
        "account_ref": "CARD-001",
        "is_active": "1",
    },
    "management.delete_payment_method": {},
    "management.add_bank": {"name": "Release Bank", "is_active": "1"},
    "management.update_bank": {"name": "Test Bank updated", "is_active": "1"},
    "management.delete_bank": {},
    "management.update_initial_saving": {"initial_saving": "1200"},
    "management.update_records_years": {"records_years": "5"},
    "management.test_db_connection": {},
    "management.save_db_connection": {},
    "management.rollback_db_connection": {},
    "management.reset_db": {},
    "management.seed_demo_data": {},
    "management.clear_demo_data": {},
    "management.toggle_user": {},
    "management.update_role": {"role": "editor"},
    "backups.backups_update_config": {"frequency": "weekly", "weekly_day": "1", "retain_count": "7"},
    "backups.backups_run_now": {},
    "backups.backups_restore_run": {},
    "backups.backups_delete_run_file": {},
}


def build_path(rule):
    def replace(match):
        name = match.group("name")
        if name not in PATH_VALUES:
            raise AssertionError(f"Missing path fixture for <{name}> in {rule.rule}")
        return PATH_VALUES[name]

    return re.sub(r"<(?:(?:int|path|string):)?(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)>", replace, rule.rule)


def route_cases(app):
    cases = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda item: (item.rule, item.endpoint)):
        if rule.endpoint in IGNORED_ENDPOINTS:
            continue
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            cases.append((rule.endpoint, method, build_path(rule)))
    return cases


def post_payload(endpoint):
    payload = dict(POST_PAYLOADS[endpoint])
    payload["csrf_token"] = CSRF_TOKEN
    return payload
