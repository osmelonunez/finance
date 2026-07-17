import os
import shutil
from datetime import datetime
from pathlib import Path

from route_manifest import IGNORED_ENDPOINTS, PUBLIC_ENDPOINTS, build_path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = Path(
    os.environ.get("FINANCE_ENDPOINT_CATALOG", ROOT / "docs" / "testing" / "endpoints.md")
)
REPORT_DIR = Path(os.environ.get("FINANCE_TEST_REPORT_DIR", ROOT / "test-reports"))

SPECIFIC_COVERAGE = {
    "categories.add_category": "test_category_create_update_delete_flow",
    "categories.update_category": "test_category_create_update_delete_flow",
    "categories.delete_category": "test_category_create_update_delete_flow",
    "movements.add_movement": "test_expense_create_edit_duplicate_delete_flow",
    "movements.edit": "test_expense_create_edit_duplicate_delete_flow",
    "movements.duplicate": "test_expense_create_edit_duplicate_delete_flow",
    "movements.delete": "test_expense_create_edit_duplicate_delete_flow",
    "loans.loan_usage_add": "test_loan_usage_create_update_delete_flow",
    "loans.loan_usage_update": "test_loan_usage_create_update_delete_flow",
    "loans.loan_usage_delete": "test_loan_usage_create_update_delete_flow",
    "management.management": "test_role_access_matrix",
    "management.management_users": "test_role_access_matrix",
    "management.management_payment_methods": "test_role_access_matrix",
    "management.payment_methods_section": "test_role_access_matrix",
    "management.bank_detail": "test_bank_detail_pagination_loads_second_page",
    "management.add_payment_method": "test_valid_card_is_created",
    "management.delete_payment_method": "test_payment_method_with_movements_cannot_be_deleted",
    "management.update_bank": "test_deactivating_bank_deactivates_linked_methods",
    "management.delete_bank": "test_bank_with_linked_methods_cannot_be_deleted",
    "backups.backups_page": "test_role_access_matrix",
}


def endpoint_rows(app):
    rows = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda item: (item.rule, item.endpoint)):
        if rule.endpoint in IGNORED_ENDPOINTS:
            continue
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            rows.append(
                {
                    "route": rule.rule,
                    "test_path": build_path(rule),
                    "method": method,
                    "endpoint": rule.endpoint,
                    "access": "Público" if rule.endpoint in PUBLIC_ENDPOINTS else "Autenticado",
                    "contract": "Sí",
                    "auth": "N/A" if rule.endpoint in PUBLIC_ENDPOINTS else "Sí",
                    "csrf": "Sí" if method == "POST" else "N/A",
                    "specific": SPECIFIC_COVERAGE.get(rule.endpoint, "—"),
                }
            )
    return rows


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_cell(value) for value in row) + " |")
    return lines


def write_catalog(app, destination=CATALOG_PATH):
    rows = endpoint_rows(app)
    rule_count = len({(row["route"], row["endpoint"]) for row in rows})
    lines = [
        "# Catálogo de endpoints y cobertura automática",
        "",
        "Este fichero se genera desde el registro de rutas de Flask. No debe editarse manualmente.",
        "",
        f"- Reglas de aplicación: **{rule_count}**.",
        f"- Combinaciones endpoint-método: **{len(rows)}**.",
        "- Se excluyen la ruta estática y los métodos automáticos `HEAD` y `OPTIONS`.",
        "- `Contrato`, `Autenticación` y `CSRF` indican que existe una comprobación automática genérica.",
        "- `Prueba específica` identifica cobertura funcional adicional; `—` significa que solo tiene cobertura genérica.",
        "",
    ]
    lines.extend(
        _table(
            [
                "Ruta",
                "Método",
                "Endpoint",
                "Acceso",
                "Contrato",
                "Autenticación",
                "CSRF",
                "Prueba específica",
            ],
            [
                (
                    f"`{row['route']}`",
                    row["method"],
                    f"`{row['endpoint']}`",
                    row["access"],
                    row["contract"],
                    row["auth"],
                    row["csrf"],
                    f"`{row['specific']}`" if row["specific"] != "—" else "—",
                )
                for row in rows
            ],
        )
    )
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def _status(results, check, row):
    if check == "auth" and row["auth"] == "N/A":
        return "N/A"
    if check == "csrf" and row["csrf"] == "N/A":
        return "N/A"
    return results.get((check, row["endpoint"], row["method"], row["test_path"]), "NO EJECUTADO")


def _specific_status(test_name, test_outcomes):
    if test_name == "—":
        return "N/A"
    matches = [
        status
        for nodeid, status in test_outcomes.items()
        if f"::{test_name}" in nodeid
    ]
    if not matches:
        return "NO EJECUTADO"
    if "FALLO" in matches:
        return "FALLO"
    if all(status == "OK" for status in matches):
        return "OK"
    return "PARCIAL"


def _overall_status(contract, auth, csrf, functional):
    required = [value for value in (contract, auth, csrf, functional) if value != "N/A"]
    if "FALLO" in required:
        return "FALLO"
    if required and all(value == "OK" for value in required):
        return "OK"
    if all(value == "NO EJECUTADO" for value in required):
        return "NO EJECUTADO"
    return "PARCIAL"


def write_execution_report(app, results, test_outcomes, exitstatus, invocation):
    rows = endpoint_rows(app)
    timestamp = datetime.now().astimezone()
    passed = sum(value == "OK" for value in test_outcomes.values())
    failed = sum(value == "FALLO" for value in test_outcomes.values())
    skipped = sum(value == "OMITIDO" for value in test_outcomes.values())
    report_rows = []
    endpoint_totals = {"OK": 0, "FALLO": 0, "PARCIAL": 0, "NO EJECUTADO": 0}
    for row in rows:
        contract = _status(results, "contract", row)
        auth = _status(results, "auth", row)
        csrf = _status(results, "csrf", row)
        functional = _specific_status(row["specific"], test_outcomes)
        overall = _overall_status(contract, auth, csrf, functional)
        endpoint_totals[overall] += 1
        report_rows.append(
            (
                f"`{row['route']}`",
                row["method"],
                f"`{row['endpoint']}`",
                row["access"],
                contract,
                auth,
                csrf,
                f"`{row['specific']}`" if row["specific"] != "—" else "—",
                functional,
                overall,
            )
        )

    lines = [
        f"# Informe de pruebas - {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
        f"- Comando pytest: `{invocation}`.",
        f"- Resultado del proceso: **{'CORRECTO' if exitstatus == 0 else 'FALLIDO'}** (código {exitstatus}).",
        f"- Pruebas: **{passed} correctas**, **{failed} fallidas**, **{skipped} omitidas**.",
        f"- Endpoint-método: **{endpoint_totals['OK']} correctos**, **{endpoint_totals['FALLO']} fallidos**, "
        f"**{endpoint_totals['PARCIAL']} parciales**, **{endpoint_totals['NO EJECUTADO']} no ejecutados**.",
        "",
        "`Resultado` es correcto cuando todas las comprobaciones aplicables de contrato, autenticación, CSRF y prueba funcional han pasado.",
        "",
    ]
    lines.extend(
        _table(
            [
                "Ruta",
                "Método",
                "Endpoint",
                "Acceso",
                "Contrato",
                "Autenticación",
                "CSRF",
                "Prueba específica",
                "Funcional",
                "Resultado",
            ],
            report_rows,
        )
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"finance-test-report-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copyfile(report_path, REPORT_DIR / "latest.md")
    return report_path


if __name__ == "__main__":
    from app import app

    path = write_catalog(app)
    print(path)
