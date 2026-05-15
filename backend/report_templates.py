from report_templates_v1 import render_report_html_v1


def _normalize_version(value: str | None) -> str:
    version = (value or "v1").strip().lower()
    return version if version in {"v1"} else "v1"


def render_report_html(template_version="v1", **kwargs):
    version = _normalize_version(template_version)
    renderers = {
        "v1": render_report_html_v1,
    }
    return renderers[version](**kwargs)
