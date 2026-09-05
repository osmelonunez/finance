import re

import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _post(client, path, data):
    return client.post(
        path,
        data={**data, "csrf_token": "test-csrf-token"},
        follow_redirects=False,
    )


def test_monthly_report_shows_summary_categories_and_top_expenses(admin_client):
    response = admin_client.get("/reports?type=monthly&period=2026-07")
    assert response.status_code == 200
    assert b"2.500,00" in response.data
    assert b"1.334,56" in response.data
    assert b"500,00" in response.data
    assert b"665,44" in response.data
    assert b"Alimentacion" in response.data
    assert b"Test expense" in response.data
    assert b"Test loan payment" in response.data


def test_yearly_report_aggregates_selected_year(admin_client):
    response = admin_client.get("/reports?type=yearly&period=2026")
    assert response.status_code == 200
    assert b"2.500,00" in response.data
    assert b"1.334,56" in response.data
    assert b'value="2026"' in response.data


def test_future_report_periods_are_clamped(admin_client):
    monthly = admin_client.get("/reports?type=monthly&period=2099-12")
    yearly = admin_client.get("/reports?type=yearly&period=2099")
    assert b'value="2026-07"' in monthly.data
    assert b'value="2026"' in yearly.data


def test_report_settings_move_to_reports(admin_client, db_query):
    response = _post(
        admin_client,
        "/reports/email-settings/save",
        {
            "monthly_enabled": "1",
            "monthly_template_version": "v7",
            "yearly_template_version": "v8",
        },
    )
    assert response.status_code in {302, 303}
    assert response.headers["Location"].endswith("/reports")
    assert db_query(
        """
        SELECT monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version
        FROM email_report_config WHERE id=1
        """
    ) == (True, False, "v7", "v8")


@pytest.mark.parametrize("version", ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"])
def test_email_template_preview_uses_real_report_data(admin_client, version):
    response = admin_client.get(
        f"/reports/template-preview?version={version}&type=monthly&period=2026-07"
    )
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "frame-ancestors 'self'" in response.headers["Content-Security-Policy"]
    assert "img-src 'self' data:" in response.headers["Content-Security-Policy"]
    assert f'data-finance-template="{version}"'.encode() in response.data
    assert b"Test expense" in response.data
    assert b"2.500,00" in response.data
    assert response.data.count(b"data-finance-period='1'") == 1
    assert b'data-finance-branding="footer"' in response.data
    assert b"FINANCE_FOOTER_SLOT" not in response.data


@pytest.mark.parametrize(
    "version",
    ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"],
)
def test_every_email_template_links_to_finance_without_showing_raw_url(
    admin_client, monkeypatch, version
):
    monkeypatch.setenv("APP_PUBLIC_URL", "https://devfinance.home")

    response = admin_client.get(
        f"/reports/template-preview?version={version}&type=monthly&period=2026-07"
    )

    assert response.status_code == 200
    assert b"href='https://devfinance.home'" in response.data
    assert "Abrir Finance</a>".encode() in response.data
    assert b">https://devfinance.home</a>" not in response.data
    assert b"Finance URL:" not in response.data
    assert "URL de Finance:".encode() not in response.data


def test_reports_show_one_grid_selector_for_ten_templates(admin_client):
    response = admin_client.get("/reports?section=templates&type=monthly&period=2026-07")
    assert response.status_code == 200
    assert b'id="monthlyTemplateVersion"' in response.data
    assert b'id="yearlyTemplateVersion"' in response.data
    assert b'id="templateStrip"' in response.data
    assert b'name="logo_url"' not in response.data
    assert b'name="contact_text"' not in response.data
    for version in ("v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"):
        assert f'value="{version}"'.encode() in response.data
        assert response.data.count(f'data-version="{version}"'.encode()) == 1


def test_email_template_branding_is_saved_and_rendered_safely(admin_client, db_query):
    saved = _post(
        admin_client,
        "/reports/email-settings/save",
        {
            "monthly_enabled": "1",
            "yearly_enabled": "1",
            "monthly_template_version": "v9",
            "yearly_template_version": "v10",
            "next_section": "templates",
            "brand_name": "Acme & Partners",
            "header_text": "Private report",
            "footer_text": "<script>alert(1)</script>",
        },
    )

    assert saved.status_code in {302, 303}
    assert db_query(
        """
        SELECT monthly_template_version, yearly_template_version, brand_name
        FROM email_report_config WHERE id=1
        """
    ) == ("v9", "v10", "Acme & Partners")

    preview = admin_client.get(
        "/reports/template-preview?version=v9&type=monthly&period=2026-07"
    )
    assert b"data-finance-branding='header'" in preview.data
    assert "Balance mensual".encode() in preview.data
    assert b"Acme &amp; Partners" in preview.data
    assert b"Acme &amp; Partners Balance mensual" in preview.data
    assert (
        b"style='display:block;margin-top:4px;font-size:.78em'>Private report</span>"
        in preview.data
    )
    assert preview.data.index(b"Private report") < preview.data.index(
        "Periodo: 2026-07".encode()
    )
    assert b'data-finance-branding="footer"' in preview.data
    assert b"text-align:center" in preview.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in preview.data
    assert b"<script>alert(1)</script>" not in preview.data


def test_email_template_preview_opens_in_an_accessible_inline_modal(admin_client):
    response = admin_client.get("/reports?section=templates&type=monthly&period=2026-07")

    assert response.status_code == 200
    assert b'id="templatePreviewModal"' in response.data
    assert b'id="templatePreviewFrame"' in response.data
    assert b'id="closeTemplatePreview"' in response.data
    assert b'aria-modal="true"' in response.data
    preview_buttons = re.findall(
        rb'<button class="btn btn-link btn-sm p-0 template-preview"[^>]*>',
        response.data,
    )
    assert len(preview_buttons) == 10
    assert all(b'type="button"' in button for button in preview_buttons)
    assert all(b'href=' not in button for button in preview_buttons)
    assert b"openTemplatePreview(button.dataset.previewUrl, button)" in response.data
    assert b"event.target === previewModal" in response.data
    assert b"event.key === 'Escape'" in response.data


def test_email_template_modal_manages_frame_scroll_focus_and_cleanup(admin_client):
    response = admin_client.get("/reports?section=templates&type=monthly&period=2026-07")

    assert response.status_code == 200
    assert b"body.template-preview-open { overflow:hidden; }" in response.data
    assert b"previewFrame.src = url" in response.data
    assert b"document.body.classList.add('template-preview-open')" in response.data
    assert b"previewClose.focus()" in response.data
    assert b"previewFrame.src = 'about:blank'" in response.data
    assert b"previewTrigger?.focus()" in response.data
    assert b"document.body.classList.remove('template-preview-open')" in response.data


def test_template_selector_builds_monthly_and_yearly_modal_urls(admin_client):
    monthly = admin_client.get(
        "/reports?section=templates&type=monthly&period=2026-07"
    )
    yearly = admin_client.get(
        "/reports?section=templates&type=yearly&period=2026"
    )

    for response in (monthly, yearly):
        assert response.status_code == 200
        assert b"button.dataset.previewUrl = `/reports/template-preview" in response.data
        assert b"activeType === 'yearly'" in response.data
        assert b"sourceType === 'yearly' ? `${rawPeriod}-01` : rawPeriod" in response.data
        assert b"data-template-type=\"monthly\"" in response.data
        assert b"data-template-type=\"yearly\"" in response.data


def test_template_preview_normalizes_invalid_arguments(admin_client):
    response = admin_client.get(
        "/reports/template-preview?version=unknown&type=weekly&period=invalid"
    )

    assert response.status_code == 200
    assert b'data-finance-template="v1"' in response.data
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "frame-ancestors 'self'" in response.headers["Content-Security-Policy"]


def test_template_preview_yearly_hides_monthly_top_expenses(admin_client):
    response = admin_client.get(
        "/reports/template-preview?version=v1&type=yearly&period=2026"
    )

    assert response.status_code == 200
    assert b'data-finance-template="v1"' in response.data
    assert b"Test expense" not in response.data
    assert b"2.500,00" in response.data


def test_only_template_preview_can_be_framed_by_same_origin(admin_client):
    preview = admin_client.get(
        "/reports/template-preview?version=v1&type=monthly&period=2026-07"
    )
    reports = admin_client.get("/reports?section=templates&type=monthly&period=2026-07")

    assert preview.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "frame-ancestors 'self'" in preview.headers["Content-Security-Policy"]
    assert reports.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in reports.headers["Content-Security-Policy"]


def test_reports_use_default_email_configuration_when_row_is_missing(
    admin_client, db_query
):
    db_query("DELETE FROM email_report_config WHERE id=1", fetch="none")

    response = admin_client.get(
        "/reports?section=templates&type=monthly&period=2026-07"
    )

    assert response.status_code == 200
    assert b'id="monthlyTemplateVersion" name="monthly_template_version" value="v1"' in response.data
    assert b'id="yearlyTemplateVersion" name="yearly_template_version" value="v1"' in response.data
    assert b'name="brand_name" maxlength="100" value="Finance"' in response.data
    assert b'name="header_text" maxlength="200" value="Personal finance report"' in response.data


def test_default_email_branding_is_configured(db_query):
    assert db_query(
        """
        SELECT brand_name, header_text, footer_text
        FROM email_report_config WHERE id=1
        """
    ) == (
        "Finance",
        "Personal finance report",
        "© {year} Osmel Nuñez Alonso · v{version} · GitHub",
    )


def test_default_email_footer_matches_site_footer(admin_client):
    preview = admin_client.get(
        "/reports/template-preview?version=v1&type=monthly&period=2026-07"
    )

    assert "Osmel Nuñez Alonso".encode() in preview.data
    assert b"v3.9.0" in preview.data
    assert b"https://github.com/osmelonunez/finance/releases/latest" in preview.data
    assert b"{year}" not in preview.data
    assert b"{version}" not in preview.data


def test_report_sections_separate_summary_templates_and_delivery_history(admin_client):
    summary = admin_client.get("/reports?section=summary&type=monthly&period=2026-07")
    delivery = admin_client.get("/reports?section=delivery&type=monthly&period=2026-07")
    templates = admin_client.get("/reports?section=templates&type=monthly&period=2026-07")

    assert b'id="reportsSummary"' in summary.data
    assert b'id="templateStrip"' not in summary.data
    assert b'id="recentEmailDeliveries"' not in summary.data

    assert b'id="emailDeliverySettings"' in delivery.data
    assert b'id="recentEmailDeliveries"' in delivery.data
    assert b'id="templateStrip"' not in delivery.data

    assert b'id="emailTemplates"' in templates.data
    assert b'id="templateStrip"' in templates.data
    assert b'id="monthlyEnabled"' not in templates.data
    assert b'id="recentEmailDeliveries"' not in templates.data


def test_month_comparison_shows_current_previous_absolute_and_percentage(admin_client, db_query):
    db_query(
        """
        INSERT INTO records (
            id, concept, amount, date, type, comment, category_id,
            payment_method_id, loan_id, is_loan_payment, created_by
        ) VALUES
            (101, 'Previous income', 2000, '2026-06', 'income', '', 2, NULL, NULL, FALSE, 'admin_test'),
            (102, 'Previous expense', 1000, '2026-06', 'expense', '', 1, 1, NULL, FALSE, 'admin_test'),
            (103, 'Previous saving', 400, '2026-06', 'saving', '', 2, NULL, NULL, FALSE, 'admin_test')
        """,
        fetch="none",
    )
    response = admin_client.get(
        "/reports?section=comparisons&comparison_scope=month&comparison_period=2026-07"
    )
    assert response.status_code == 200
    assert b'id="reportComparisons"' in response.data
    assert b"2026-07" in response.data
    assert b"2026-06" in response.data
    assert b"2.500,00" in response.data
    assert b"2.000,00" in response.data
    assert b"+500,00" in response.data
    assert b"+25.0%" in response.data


@pytest.mark.parametrize(
    "scope,period,current_label,previous_label",
    [
        ("quarter", "2026-Q3", b'value="2026-Q3"', b'value="2026-Q2"'),
        ("year", "2026", b"2026", b"2025"),
    ],
)
def test_quarter_and_year_comparisons_use_immediately_previous_period(
    admin_client, scope, period, current_label, previous_label
):
    response = admin_client.get(
        f"/reports?section=comparisons&comparison_scope={scope}&comparison_period={period}"
    )
    assert response.status_code == 200
    assert current_label in response.data
    assert previous_label in response.data
    assert b"2.500,00" in response.data


def test_comparison_allows_selecting_an_arbitrary_reference_period(admin_client):
    response = admin_client.get(
        "/reports?section=comparisons&comparison_scope=year"
        "&comparison_period=2026&comparison_against=2024"
    )
    assert response.status_code == 200
    assert b'name="comparison_period"' in response.data
    assert b'name="comparison_against"' in response.data
    assert b'value="2026"' in response.data
    assert b'value="2024"' in response.data
    assert b"2024:" in response.data


@pytest.mark.parametrize(
    "scope,expected_options",
    [
        ("month", (b"Jul 2026", b"Dic 2025")),
        ("quarter", (b"2026 T3", b"2025 T4")),
        ("year", (b'value="2026"', b'value="2024"')),
    ],
)
def test_comparison_periods_are_selectors_from_configured_year_window(
    admin_client, scope, expected_options
):
    response = admin_client.get(
        f"/reports?section=comparisons&comparison_scope={scope}"
    )
    assert response.status_code == 200
    assert b'<select class="form-select" id="comparisonPeriod"' in response.data
    assert b'<select class="form-select" id="comparisonAgainst"' in response.data
    for expected in expected_options:
        assert expected in response.data


@pytest.mark.parametrize(
    "evolution_range,first_label,last_label",
    [
        ("6m", b"Feb 2026", b"Jul 2026"),
        ("12m", b"Ago 2025", b"Jul 2026"),
        ("years", b"2024", b"2026"),
    ],
)
def test_financial_evolution_supports_six_twelve_months_and_years(
    admin_client, evolution_range, first_label, last_label
):
    response = admin_client.get(
        f"/reports?section=evolution&evolution_range={evolution_range}"
    )
    assert response.status_code == 200
    assert b'id="financialEvolution"' in response.data
    assert b'id="financialEvolutionChart"' in response.data
    assert first_label in response.data
    assert last_label in response.data
    assert b'"income": 2500.0' in response.data
    assert b'"expense": 1334.56' in response.data
    assert b'"saving": 500.0' in response.data
    assert b'"balance": 665.44' in response.data


def test_financial_evolution_exposes_four_series_toggles(admin_client):
    response = admin_client.get("/reports?section=evolution")
    for series in ("income", "expense", "saving", "balance"):
        assert f'value="{series}"'.encode() in response.data
    assert response.data.count(b"evolution-series") >= 4


def test_mom_automatically_compares_with_previous_month(admin_client):
    response = admin_client.get(
        "/reports?section=comparisons&comparison_mode=mom&comparison_period=2026-07"
    )
    assert response.status_code == 200
    assert b'<option value="mom" selected>MoM' in response.data
    assert b'id="comparisonKind" name="comparison_kind"' in response.data
    assert b'id="comparisonAgainst" name="comparison_against" disabled' in response.data
    assert b'value="2026-06" selected' in response.data


def test_yoy_category_breakdown_and_largest_changes(admin_client, db_query):
    db_query(
        """
        INSERT INTO records (
            id, concept, amount, date, type, comment, category_id,
            payment_method_id, loan_id, is_loan_payment, created_by
        ) VALUES
            (111, 'Prior year food', 900, '2025-07', 'expense', '', 1, 1, NULL, FALSE, 'admin_test'),
            (112, 'Prior year unused', 300, '2025-07', 'expense', '', 3, 1, NULL, FALSE, 'admin_test'),
            (113, 'Current transport', 100, '2026-07', 'expense', '', 2, 1, NULL, FALSE, 'admin_test')
        """,
        fetch="none",
    )
    response = admin_client.get(
        "/reports?section=comparisons&comparison_mode=yoy"
        "&comparison_scope=month&comparison_period=2026-07"
    )
    assert response.status_code == 200
    assert b'<option value="yoy_month" selected>YoY' in response.data
    assert b'value="2025-07" selected' in response.data
    assert b'id="categoryComparisonTable"' in response.data
    assert b"Alimentacion" in response.data
    assert b"Unused" in response.data
    assert b"Transporte" in response.data
    assert b"+434,56" in response.data
    assert b"-300,00" in response.data
    assert b"Nueva" in response.data
    assert b"Sin gasto actual" in response.data


def test_comparison_type_unifies_mode_and_period_scope(admin_client):
    response = admin_client.get("/reports?section=comparisons")
    assert b'id="comparisonMode"' not in response.data
    assert b'id="comparisonScope"' not in response.data
    for kind in (
        "free_month", "free_quarter", "free_year", "mom",
        "yoy_month", "yoy_quarter", "yoy_year",
    ):
        assert f'<option value="{kind}"'.encode() in response.data


def test_yoy_quarter_and_year_modes_select_previous_year(admin_client):
    quarter = admin_client.get(
        "/reports?section=comparisons&comparison_kind=yoy_quarter"
        "&comparison_period=2026-Q3"
    )
    year = admin_client.get(
        "/reports?section=comparisons&comparison_kind=yoy_year"
        "&comparison_period=2026"
    )

    assert quarter.status_code == 200
    assert b'value="2025-Q3" selected' in quarter.data
    assert year.status_code == 200
    assert b'value="2025" selected' in year.data


def test_out_of_window_comparison_period_remains_selectable(admin_client):
    response = admin_client.get(
        "/reports?section=comparisons&comparison_kind=free_year"
        "&comparison_period=2000&comparison_against=2001"
    )

    assert response.status_code == 200
    assert b'value="2000" selected' in response.data
    assert b'value="2001" selected' in response.data


def test_invalid_report_options_fall_back_to_safe_defaults(admin_client):
    summary = admin_client.get(
        "/reports?section=unknown&type=weekly&period=invalid"
    )
    comparisons = admin_client.get(
        "/reports?section=comparisons&comparison_scope=decade"
        "&comparison_mode=invalid&evolution_range=invalid"
    )

    assert summary.status_code == 200
    assert b'id="reportsSummary"' in summary.data
    assert b'<option value="monthly" selected>' in summary.data
    assert comparisons.status_code == 200
    assert b'id="reportComparisons"' in comparisons.data
    assert b'<option value="free_month" selected>' in comparisons.data


def test_invalid_yearly_period_falls_back_to_current_year(admin_client):
    response = admin_client.get("/reports?type=yearly&period=not-a-year")

    assert response.status_code == 200
    assert b'value="2026"' in response.data


def test_category_and_bank_filters_apply_to_report_data(admin_client, db_query):
    db_query(
        """
        INSERT INTO records (
            id, concept, amount, date, type, comment, category_id,
            payment_method_id, loan_id, is_loan_payment, created_by
        ) VALUES
            (121, 'Filtered transport', 50, '2026-07', 'expense', '', 2, 3, NULL, FALSE, 'admin_test')
        """,
        fetch="none",
    )
    by_category = admin_client.get(
        "/reports?section=summary&type=monthly&period=2026-07&category_id=2"
    )
    by_bank = admin_client.get(
        "/reports?section=summary&type=monthly&period=2026-07&bank_id=2"
    )
    for response in (by_category, by_bank):
        assert response.status_code == 200
        assert b"50,00" in response.data
        assert b"1.334,56" not in response.data
        assert b"Exportar CSV" in response.data


@pytest.mark.parametrize(
    "filter_query,expected_expense",
    [
        ("account_id=2", b"1.334,56"),
        ("card_id=1", b"1.234,56"),
        ("loan_id=1", b"100,00"),
        ("loan_id=none", b"1.234,56"),
    ],
)
def test_account_card_and_loan_filters(admin_client, filter_query, expected_expense):
    response = admin_client.get(
        f"/reports?section=summary&type=monthly&period=2026-07&{filter_query}"
    )
    assert response.status_code == 200
    assert expected_expense in response.data
    assert b'id="reportAccountFilter"' in response.data
    assert b'id="reportCardFilter"' in response.data
    assert b'id="reportLoanFilter"' in response.data


@pytest.mark.parametrize(
    "query,expected_header,expected_filename",
    [
        ("section=summary&type=monthly&period=2026-07", b"metric,amount", b"finance-summary-2026-07.csv"),
        ("section=comparisons&comparison_kind=mom&comparison_period=2026-07", b"metric,current,comparison", b"finance-comparison-2026-07.csv"),
        ("section=evolution&evolution_range=6m", b"period,income,expense,saving,balance", b"finance-evolution-6m.csv"),
    ],
)
def test_csv_export_uses_contextual_report_data(
    admin_client, query, expected_header, expected_filename
):
    response = admin_client.get(f"/reports/export.csv?{query}")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert expected_header in response.data
    assert expected_filename in response.headers["Content-Disposition"].encode()


def test_csv_and_print_normalize_invalid_ranges_and_types(admin_client):
    csv_response = admin_client.get(
        "/reports/export.csv?section=evolution&evolution_range=invalid"
    )
    print_response = admin_client.get(
        "/reports/print?section=evolution&evolution_range=invalid"
    )
    summary_csv = admin_client.get(
        "/reports/export.csv?section=unknown&type=weekly&period=invalid"
    )

    assert csv_response.status_code == 200
    assert b'filename="finance-evolution-6m.csv"' in csv_response.headers[
        "Content-Disposition"
    ].encode()
    assert print_response.status_code == 200
    assert b"Feb 2026" in print_response.data
    assert summary_csv.status_code == 200
    assert b'filename="finance-summary-2026-07.csv"' in summary_csv.headers[
        "Content-Disposition"
    ].encode()


def test_print_view_lists_valid_category_and_bank_filters(admin_client):
    response = admin_client.get(
        "/reports/print?section=summary&type=monthly&period=2026-07"
        "&category_id=1&bank_id=1"
    )

    assert response.status_code == 200
    assert b"Alimentacion" in response.data
    assert b"Test Bank" in response.data


def test_user_can_save_open_and_delete_report_configuration(admin_client, db_query):
    saved = _post(
        admin_client,
        "/reports/saved/save",
        {
            "name": "Mi comparativa",
            "section": "comparisons",
            "query_string": (
                "section=comparisons&comparison_kind=yoy_month"
                "&comparison_period=2026-07&category_id=1&bank_id=1"
            ),
        },
    )
    assert saved.status_code in {302, 303}
    assert saved.headers["Location"].endswith("/reports?section=saved")
    row = db_query(
        "SELECT id, name, section, query_string FROM saved_reports WHERE user_id=1"
    )
    assert row[1:] == (
        "Mi comparativa",
        "comparisons",
        "section=comparisons&comparison_kind=yoy_month&comparison_period=2026-07&category_id=1&bank_id=1",
    )

    listing = admin_client.get("/reports?section=saved")
    assert b'id="savedReports"' in listing.data
    assert b"Mi comparativa" in listing.data
    assert b"comparison_kind=yoy_month" in listing.data

    deleted = _post(admin_client, f"/reports/saved/{row[0]}/delete", {})
    assert deleted.status_code in {302, 303}
    assert db_query("SELECT COUNT(*) FROM saved_reports WHERE user_id=1") == (0,)


@pytest.mark.parametrize(
    "query,expected",
    [
        ("section=summary&type=monthly&period=2026-07", b"2.500,00"),
        ("section=comparisons&comparison_kind=mom&comparison_period=2026-07", b"Alimentacion"),
        ("section=evolution&evolution_range=6m", b"Jul 2026"),
    ],
)
def test_print_view_is_purpose_built_for_pdf(admin_client, query, expected):
    response = admin_client.get(f"/reports/print?{query}")
    assert response.status_code == 200
    assert b"window.print()" in response.data
    assert b"@media print" in response.data
    assert b"navbar" not in response.data
    assert expected in response.data


def test_regular_user_can_view_reports_but_not_configuration(client, login_as):
    login_as(client, "user")
    response = client.get("/reports?type=monthly&period=2026-07")
    assert response.status_code == 200
    assert b"/reports/email-settings/save" not in response.data

    denied = _post(
        client,
        "/reports/email-settings/save",
        {"monthly_enabled": "1"},
    )
    assert denied.status_code in {302, 303}
    assert denied.headers["Location"].endswith("/")


def test_email_delivery_shows_environment_smtp_status(admin_client, monkeypatch):
    monkeypatch.setenv("SMTP_ENABLED", "false")
    response = admin_client.get("/reports?section=delivery")
    assert response.status_code == 200
    assert b"SMTP disabled" in response.data or b"SMTP desactivado" in response.data
    assert b"/management/smtp" not in response.data
