from html import escape
from datetime import datetime
import os

from report_templates_v1 import _public_url, render_report_html_v1
from report_templates_extra import (
    render_report_html_v4,
    render_report_html_v5,
    render_report_html_v6,
    render_report_html_v7,
    render_report_html_v8,
    render_report_html_v9,
    render_report_html_v10,
)


def _normalize_version(value: str | None) -> str:
    version = (value or "v1").strip().lower()
    return version if version in {"v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"} else "v1"


def _apply_branding(
    html,
    branding,
    report_title="",
    period_label="",
    period_caption="Period",
    open_finance_text="Open Finance",
):
    branding = branding or {}
    brand_name = escape((branding.get("brand_name") or "").strip())
    header_text = escape((branding.get("header_text") or "").strip())
    raw_footer_text = (branding.get("footer_text") or "").strip()
    footer_text = escape(
        raw_footer_text
        .replace("{year}", str(datetime.now().year))
        .replace("{version}", os.environ.get("APP_VERSION", "3.8.1"))
    )
    if raw_footer_text == "© {year} Osmel Nuñez Alonso · v{version} · GitHub":
        footer_text = footer_text.rsplit("GitHub", 1)[0] + (
            "<a href='https://github.com/osmelonunez/finance/releases/latest' "
            "style='color:inherit;text-decoration:none'>GitHub</a>"
        )
    accent = "#fd7e14"
    public_url = _public_url()
    site_link = ""
    if public_url:
        site_link = (
            f"<div style='margin-bottom:8px'><a href='{escape(public_url, quote=True)}' "
            f"style='color:inherit;font-weight:700;text-decoration:none'>"
            f"{escape(open_finance_text)}</a></div>"
        )

    if report_title:
        combined_title = " ".join(
            item for item in (brand_name, escape(report_title)) if item
        )
        period_text = " ".join(
            item for item in (
                f"{escape(period_caption)}:" if period_caption else "",
                escape(period_label),
            ) if item
        )
        branded_title = (
            f"<span data-finance-branding='header' style='display:block'>"
            f"<span style='display:block'>{combined_title}</span>"
            f"<span style='display:block;margin-top:4px;font-size:.78em'>{header_text}</span>"
            f"<span data-finance-period='1' style='display:block;margin-top:4px;font-size:.64em;"
            f"font-weight:400'>{period_text}</span></span>"
        )
        html = html.replace(escape(report_title), branded_title, 1)

    if footer_text or site_link:
        footer = f"""
        <div data-finance-branding="footer" style="margin-top:14px;padding-top:12px;border-top:2px solid {accent};color:#4b5563;font:12px Arial,sans-serif;text-align:center">
          {site_link}
          <div>{footer_text}</div>
        </div>"""
        if "<!-- FINANCE_FOOTER_SLOT -->" in html:
            html = html.replace("<!-- FINANCE_FOOTER_SLOT -->", footer, 1)
        else:
            html = re.sub(
                r"</body>",
                lambda _match: footer + "</body>",
                html,
                count=1,
                flags=re.I,
            )
    else:
        html = html.replace("<!-- FINANCE_FOOTER_SLOT -->", "", 1)
    return html


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
    branding = kwargs.pop("branding", None)
    report_title = kwargs.get("title") or ""
    period_label = kwargs.get("period_label") or ""
    period_caption = (kwargs.get("texts") or {}).get("period", "Period")
    open_finance_text = (kwargs.get("texts") or {}).get("open_finance", "Open Finance")
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
        "v9": render_report_html_v9,
        "v10": render_report_html_v10,
    }
    html = renderers[version](**kwargs)
    if version == "v1":
        html = html.replace("<html>", '<html data-finance-template="v1">', 1)
    return _apply_branding(
        html,
        branding,
        report_title,
        period_label,
        period_caption,
        open_finance_text,
    )
