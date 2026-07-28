from i18n import t


def test_domain_catalogues_preserve_existing_budget_and_management_translations():
    assert t("Budgets", "es") == "Presupuestos"
    assert t("Remove budget", "es") == "Quitar presupuesto"
    assert t("Modules", "es") == "Módulos"
    assert t("Enable loans module", "es") == "Activar módulo de préstamos"


def test_unknown_translation_keeps_english_source_text():
    assert t("A future untranslated key", "es") == "A future untranslated key"
