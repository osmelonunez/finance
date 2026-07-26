from report_templates_v1 import render_report_html_v1
from report_templates_extra import (
    render_report_html_v4,
    render_report_html_v5,
    render_report_html_v6,
    render_report_html_v7,
    render_report_html_v8,
)


def _normalize_version(value: str | None) -> str:
    version = (value or "v1").strip().lower()
    return version if version in {"v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8"} else "v1"


def _render_with_palette(renderer, replacements, marker, **kwargs):
    html = renderer(**kwargs)
    for source, target in replacements.items():
        html = html.replace(source, target)
    return html.replace("<html>", f'<html data-finance-template="{marker}">', 1)


def _render_v2(**kwargs):
    return _render_with_palette(
        render_report_html_v1,
        {
            "#f6f8fb": "#f1f8f6",
            "#4f88b8": "#167d72",
            "#7ea8ca": "#45a89a",
            "#3f78a8": "#167d72",
            "#f8fbff": "#f2fbf8",
            "#dfe7f0": "#cfe5df",
            "#f1f5fa": "#eaf6f2",
            "#e5ebf2": "#d7e9e4",
        },
        "v2",
        **kwargs,
    )


def _render_v3(**kwargs):
    return _render_with_palette(
        render_report_html_v1,
        {
            "#f6f8fb": "#e9edf3",
            "#ffffff": "#fffdf8",
            "#4f88b8": "#172b4d",
            "#7ea8ca": "#355070",
            "#3f78a8": "#8a641f",
            "#f8fbff": "#fff8e8",
            "#dfe7f0": "#d9c99f",
            "#f1f5fa": "#f4ecd8",
            "#e5ebf2": "#e4d7b5",
            "#e79831": "#b6862c",
        },
        "v3",
        **kwargs,
    )


def render_report_html(template_version="v1", **kwargs):
    version = _normalize_version(template_version)
    renderers = {
        "v1": render_report_html_v1,
        "v2": _render_v2,
        "v3": _render_v3,
        "v4": render_report_html_v4,
        "v5": render_report_html_v5,
        "v6": render_report_html_v6,
        "v7": render_report_html_v7,
        "v8": render_report_html_v8,
    }
    html = renderers[version](**kwargs)
    if version == "v1":
        html = html.replace("<html>", '<html data-finance-template="v1">', 1)
    return html
