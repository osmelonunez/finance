from datetime import datetime
from io import BytesIO
import re

import pytest
from openpyxl import Workbook


pytestmark = [pytest.mark.integration]


def _ing_xlsx(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Movimientos"
    sheet.append(("Movimientos de la Cuenta", "", "Número de cuenta:", "1234"))
    sheet.append(("", "", "Titular:", "Test"))
    sheet.append(("", "", "Fecha exportación:", "27/08/2026"))
    sheet.append(("F. VALOR", "CATEGORÍA", "SUBCATEGORÍA", "DESCRIPCIÓN", "COMENTARIO", "IMPORTE (€)", "SALDO (€)"))
    for row in rows:
        sheet.append(row)
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def test_expense_page_links_to_integrated_import_page(admin_client):
    response = admin_client.get("/records/expense")
    assert response.status_code == 200
    assert b'href="/records/expense/import"' in response.data

    import_page = admin_client.get("/records/expense/import")
    assert import_page.status_code == 200
    assert b"Importar registros" in import_page.data
    assert b"Importar gastos desde Excel" not in import_page.data
    assert b"Selecciona el extracto de ING" in import_page.data
    assert b'value="ing"' in import_page.data
    assert b"Formato del banco" not in import_page.data
    assert b'accept=".xls,.xlsx"' in import_page.data


def test_income_page_links_to_income_import(admin_client):
    response = admin_client.get("/records/income")
    assert response.status_code == 200
    assert b'href="/records/income/import"' in response.data
    assert response.data.count(b'href="/records/add?from=income"') == 1
    assert b'name="date"' in response.data

    import_page = admin_client.get("/records/income/import")
    assert import_page.status_code == 200
    assert b'action="/records/income/import/preview"' in import_page.data
    assert b"Volver a ingresos" in import_page.data


def test_expense_template_is_downloadable(admin_client):
    response = admin_client.get("/records/expense/import/template")
    assert response.status_code == 200
    assert response.data.startswith(b"PK")


def test_ing_preview_maps_columns_and_flags_unknown_categories(admin_client, db_query):
    db_query(
        """
        INSERT INTO categories (name, description)
        VALUES ('Home', ''), ('Health', ''), ('Leisure', ''), ('Subscriptions', '')
        """,
        fetch="none",
    )
    response = admin_client.post(
        "/records/expense/import/preview",
        data={
            "csrf_token": "test-csrf-token",
            "bank_format": "ing",
            "excel_file": (_ing_xlsx([
                (datetime(2026, 8, 27), "Alimentaci\u00f3n", "Supermercados", "Pago en AHORRAMAS 1317 MEJORADA", "ignored", -42.75, 100),
                (datetime(2026, 8, 26), "Compras", "Otros", "Pago en WWW.AMAZON*ABC123", "ignored", -10, 110),
                (datetime(2026, 8, 25), "Compras", "Otros", "Pago en WWW.AMAZON*SECOND", "ignored", -4, 114),
                (datetime(2026, 8, 26), "Vehículo y transporte", "Taxi", "Pago en UBR* PENDING.UBER.COM AMSTERDAM NL", "ignored", -12, 122),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en METRO DE MADRID S.A.", "ignored", -2, 124),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en BILL SENCILLO AVANZA CRTMMADRID ES", "ignored", -3, 127),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en FARMACIA CENTRAL", "ignored", -8, 135),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en Pizzeria Napolitana", "ignored", -11, 146),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en SANTAGLORIA ALICANTE ES", "ignored", -6, 152),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en STARBUCKS PLENILUNIO", "ignored", -7, 159),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en CAFETERIA VIPS MADRID", "ignored", -9, 168),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en APPLE.COMBILL CORK IE", "ignored", -3.99, 172),
                (datetime(2026, 8, 26), "Sin categoría", "Otros", "Pago en EMPRESA MUNICIPAL EMT MADRID ES", "ignored", -1.5, 174),
                (datetime(2026, 8, 26), "Otros gastos", "Otros", "Recibo PayPal (Europe) S.a r.l. et Cie, S.C.A.", "ignored", -6, 180),
                (datetime(2026, 8, 26), "Alimentación", "Otros", "Pago en NYX*ASONIKSYSTEMSL Valencia ES", "ignored", -3, 183),
                (datetime(2026, 8, 26), "Compras", "Otros", "Tienda desconocida", "ignored", -5, 140),
                (datetime(2026, 8, 25), "Otros ingresos", "Bizum", "Bizum recibido", "ignored", 20, 130),
                (datetime(2026, 8, 25), "Otros ingresos", "Otros", "Devolución Tarjeta WWW.AMAZON*ABC123", "ignored", 3, 133),
            ]), "movements.xls.xlsx"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b'value="AHORRAMAS"' in response.data
    assert b'value="Amazon"' in response.data
    assert b"3 movimientos agrupados" in response.data
    assert b"Ver movimientos agrupados" in response.data
    assert b"WWW.AMAZON*ABC123" in response.data
    assert b"WWW.AMAZON*SECOND" in response.data
    assert b'name="comment_5" maxlength="500"' in response.data
    assert b'name="comment_5" rows=' not in response.data
    assert b'name="amount_6" value="11"' in response.data
    assert b"Devoluci\xc3\xb3n Tarjeta WWW.AMAZON*ABC123" in response.data
    assert b'value="Uber"' in response.data
    assert b"PENDING.UBER.COM" not in response.data
    html = response.get_data(as_text=True)
    assert b'value="iCloud"' in response.data
    assert b"APPLE.COMBILL" not in response.data
    assert b'value="PayPal"' in response.data
    assert b"PayPal (Europe)" not in response.data
    assert b'value="NYX ASONIKSYSTEMSL Valencia ES"' in response.data
    assert b"Unsupported characters removed" not in response.data
    expected_categories = {
        5: "1", 6: "4", 8: "2", 9: "2", 10: "2", 11: "5",
        12: "6", 13: "6", 14: "6", 15: "6", 16: "7", 17: "2",
    }
    for source_row, category_id in expected_categories.items():
        assert re.search(
            rf'name="category_{source_row}".*?<option value="{category_id}" selected',
            html,
            re.DOTALL,
        )
    assert b"La categor\xc3\xada necesita correspondencia" in response.data
    assert b"category-mapping-warning" in response.data
    assert b"updateCategoryState" in response.data
    assert b"1 movimientos positivos" in response.data
    assert b"Mostrar movimientos positivos detectados" in response.data
    assert b"Bizum recibido" in response.data
    assert b"Ingreso" in response.data
    assert b"ignored" not in response.data
    assert b"Nuestra categor\xc3\xada" not in response.data
    assert b"Eliminar de la previsualizaci\xc3\xb3n" in response.data
    assert b"Tarjeta para todos los gastos" in response.data
    assert b"Test Card" in response.data
    assert b"Inactive Card" not in response.data


def test_confirm_import_inserts_only_selected_expenses(admin_client, db_query):
    response = admin_client.post(
        "/records/expense/import",
        data={
            "csrf_token": "test-csrf-token",
            "bank_format": "ing",
            "payment_method_id": "1",
            "selected_rows": ["5", "6"],
            "concept_5": "Groceries",
            "amount_5": "42.75",
            "date_5": "2026-08",
            "category_5": "1",
            "comment_5": "Weekly household shopping",
            "concept_6": "Bus",
            "amount_6": "10",
            "date_6": "2026-08",
            "category_6": "2",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"2 gastos a\xc3\xb1adidos" in response.data
    rows = db_query(
        "SELECT concept, amount, date, type, category_id, payment_method_id, comment FROM records WHERE concept IN ('Groceries', 'Bus') ORDER BY concept",
        fetch="all",
    )
    assert len(rows) == 2
    assert all(row[3] == "expense" for row in rows)
    assert all(row[5] == 1 for row in rows)
    assert next(row for row in rows if row[0] == "Groceries")[6] == "Weekly household shopping"


def test_invalid_confirmation_prevents_the_whole_import(admin_client, db_query):
    response = admin_client.post(
        "/records/expense/import",
        data={
            "csrf_token": "test-csrf-token",
            "payment_method_id": "1",
            "selected_rows": ["5", "6"],
            "concept_5": "Valid",
            "amount_5": "10",
            "date_5": "2026-08",
            "category_5": "1",
            "concept_6": "Invalid",
            "amount_6": "-2",
            "date_6": "bad-date",
            "category_6": "999",
        },
    )
    assert response.status_code == 400
    assert b"Row 6" in response.data
    assert db_query("SELECT COUNT(*) FROM records WHERE concept='Valid'")[0] == 0


def test_confirmation_requires_an_active_card(admin_client, db_query):
    response = admin_client.post(
        "/records/expense/import",
        data={
            "csrf_token": "test-csrf-token",
            "selected_rows": ["5"],
            "concept_5": "Groceries",
            "amount_5": "10",
            "date_5": "2026-08",
            "category_5": "1",
        },
    )
    assert response.status_code == 400
    assert b"Select an active card" in response.data
    assert db_query("SELECT COUNT(*) FROM records WHERE concept='Groceries'")[0] == 0


def test_income_preview_shows_positive_movements_and_unchecks_transfers(admin_client):
    response = admin_client.post(
        "/records/income/import/preview",
        data={
            "csrf_token": "test-csrf-token",
            "bank_format": "ing",
            "excel_file": (_ing_xlsx([
                (datetime(2026, 8, 25), "Otros ingresos", "Bizum", "Bizum recibido", "", 20, 130),
                (datetime(2026, 8, 24), "Otros ingresos", "Otros", "Devolución compra", "", 5, 125),
                (datetime(2026, 8, 23), "Movimientos excluidos", "Transferencia", "Traspaso propio", "", 100, 25),
                (datetime(2026, 8, 22), "Otros ingresos", "Otros", "Devolución Tarjeta WWW.AMAZON*ORDER", "", 7, 18),
            ]), "movements.xlsx"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Revisar ingresos antes de importar" in response.data
    assert b"Bizum recibido" in response.data
    assert b"Devoluci\xc3\xb3n" in response.data
    assert b"Transferencia" in response.data
    assert b"WWW.AMAZON" not in response.data
    html = response.get_data(as_text=True)
    assert re.search(r'value="5" checked', html)
    assert re.search(r'value="7"(?! checked)', html)
    assert b"Cuenta para todos los ingresos" not in response.data


def test_confirm_income_imports_selected_rows_with_optional_account(admin_client, db_query):
    response = admin_client.post(
        "/records/income/import",
        data={
            "csrf_token": "test-csrf-token",
            "bank_format": "ing",
            "selected_rows": ["5", "6"],
            "concept_5": "Salary",
            "amount_5": "2500",
            "date_5": "2026-08",
            "comment_5": "August payroll",
            "concept_6": "Refund",
            "amount_6": "12.50",
            "date_6": "2026-08",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"2 ingresos a\xc3\xb1adidos" in response.data
    rows = db_query(
        "SELECT concept, amount, type, category_id, payment_method_id, comment FROM records WHERE concept IN ('Salary', 'Refund') ORDER BY concept",
        fetch="all",
    )
    assert len(rows) == 2
    assert all(row[2] == "income" and row[3] is None and row[4] is None for row in rows)
