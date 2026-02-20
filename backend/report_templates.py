import os


def _public_url() -> str:
    return (os.environ.get("APP_PUBLIC_URL") or "").strip().rstrip("/")


def render_report_html_v1(
    title,
    period_label,
    income,
    expense,
    saving,
    balance,
    top_expenses,
    category_summary,
    texts,
    include_top_expenses=True,
):
    max_value = max(float(income), float(expense), float(saving), 1.0)

    def bar_width(value):
        return max(2, int((float(value) / max_value) * 100))

    rows_html = ""
    for idx, row in enumerate(top_expenses, start=1):
        concept, total_amount = row[0], float(row[1] or 0)
        rows_html += (
            f"<tr>"
            f"<td style='padding:8px 10px;border-bottom:1px solid #edf1f5;color:#2f3b47;'>{idx}</td>"
            f"<td style='padding:8px 10px;border-bottom:1px solid #edf1f5;color:#2f3b47;word-break:break-word;overflow-wrap:anywhere;'>{concept}</td>"
            f"<td style='padding:8px 10px;border-bottom:1px solid #edf1f5;color:#2f3b47;text-align:right;'>{total_amount:.2f}</td>"
            f"</tr>"
        )
    if not rows_html:
        rows_html = (
            "<tr>"
            f"<td colspan='3' style='padding:10px;color:#5a6b7b;text-align:center;'>{texts['no_expense_data']}</td>"
            "</tr>"
        )

    category_rows_html = ""
    for idx, row in enumerate(category_summary, start=1):
        category_name, total_amount = row[0], float(row[1] or 0)
        category_rows_html += (
            f"<tr>"
            f"<td style='padding:8px 10px;border-bottom:1px solid #edf1f5;color:#2f3b47;'>{idx}</td>"
            f"<td style='padding:8px 10px;border-bottom:1px solid #edf1f5;color:#2f3b47;word-break:break-word;overflow-wrap:anywhere;'>{category_name}</td>"
            f"<td style='padding:8px 10px;border-bottom:1px solid #edf1f5;color:#2f3b47;text-align:right;'>{total_amount:.2f}</td>"
            f"</tr>"
        )
    if not category_rows_html:
        category_rows_html = (
            "<tr>"
            f"<td colspan='3' style='padding:10px;color:#5a6b7b;text-align:center;'>{texts['no_category_data']}</td>"
            "</tr>"
        )

    top_expenses_section = ""
    if include_top_expenses:
        top_expenses_section = f"""
        <div style="font-weight:700;color:#2f3b47;margin:14px 0 8px 0;">{texts['top_expenses']}</div>
        <table width="100%" cellpadding="0" cellspacing="0" style="width:100%;table-layout:auto;border-collapse:collapse;border:1px solid #e5ebf2;border-radius:10px;overflow:hidden;">
          <thead>
            <tr style="background:#f1f5fa;">
              <th style="padding:8px 10px;text-align:left;color:#4a5a6a;font-size:12px;">#</th>
              <th style="padding:8px 10px;text-align:left;color:#4a5a6a;font-size:12px;">{texts['concept']}</th>
              <th style="padding:8px 10px;text-align:right;color:#4a5a6a;font-size:12px;">{texts['amount']}</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
        """

    public_url = _public_url()
    open_finance_block = ""
    footer_link_block = ""
    if public_url:
        open_finance_block = f"""
        <div style="margin:12px 0 14px 0;">
          <a href="{public_url}" style="display:inline-block;background:#4f88b8;color:#ffffff;text-decoration:none;padding:9px 12px;border-radius:8px;font-weight:600;">
            {texts['open_finance']}
          </a>
        </div>
        """
        footer_link_block = f"""
        <div style="margin-top:14px;color:#5a6b7b;font-size:12px;">
          {texts['finance_url']}: <a href="{public_url}" style="color:#3f78a8;text-decoration:none;">{public_url}</a>
        </div>
        """

    return f"""
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="margin:0;padding:18px;background:#f6f8fb;font-family:Arial,sans-serif;">
    <div style="width:100%;margin:0 auto;background:#ffffff;border:1px solid #dfe7f0;border-radius:12px;overflow:hidden;">
      <div style="padding:16px 18px;background:linear-gradient(90deg,#4f88b8,#7ea8ca);color:#ffffff;">
        <div style="font-size:20px;font-weight:700;">{title}</div>
        <div style="font-size:13px;opacity:.95;margin-top:2px;">{texts['period']}: {period_label}</div>
      </div>
      <div style="padding:16px 18px;">
        {open_finance_block}
        <div style="font-weight:700;color:#2f3b47;margin-bottom:10px;">{texts['summary_title']}</div>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:14px;">
          <tr>
            <td style="width:92px;color:#2f3b47;padding:6px 0;">{texts['income']}</td>
            <td style="padding:6px 0;">
              <div style="height:14px;background:#e7f4ec;border-radius:7px;overflow:hidden;">
                <div style="height:14px;width:{bar_width(income)}%;background:#29a35f;"></div>
              </div>
            </td>
            <td style="width:100px;text-align:right;color:#1e7f4a;padding-left:8px;">{float(income):.2f}</td>
          </tr>
          <tr>
            <td style="width:92px;color:#2f3b47;padding:6px 0;">{texts['expense']}</td>
            <td style="padding:6px 0;">
              <div style="height:14px;background:#fbe9ea;border-radius:7px;overflow:hidden;">
                <div style="height:14px;width:{bar_width(expense)}%;background:#d74c4c;"></div>
              </div>
            </td>
            <td style="width:100px;text-align:right;color:#b13636;padding-left:8px;">{float(expense):.2f}</td>
          </tr>
          <tr>
            <td style="width:92px;color:#2f3b47;padding:6px 0;">{texts['saving']}</td>
            <td style="padding:6px 0;">
              <div style="height:14px;background:#fff2dd;border-radius:7px;overflow:hidden;">
                <div style="height:14px;width:{bar_width(saving)}%;background:#e79831;"></div>
              </div>
            </td>
            <td style="width:100px;text-align:right;color:#b06a17;padding-left:8px;">{float(saving):.2f}</td>
          </tr>
        </table>

        <div style="padding:10px 12px;border:1px solid #dfe7f0;border-radius:10px;background:#f8fbff;margin-bottom:14px;">
          <span style="color:#5a6b7b;">{texts['balance']}:</span>
          <span style="font-weight:700;color:{'#1e7f4a' if float(balance) >= 0 else '#b13636'};margin-left:6px;">{float(balance):.2f}</span>
        </div>

        <div style="font-weight:700;color:#2f3b47;margin:14px 0 8px 0;">{texts['category_summary']}</div>
        <table width="100%" cellpadding="0" cellspacing="0" style="width:100%;table-layout:auto;border-collapse:collapse;border:1px solid #e5ebf2;border-radius:10px;overflow:hidden;">
          <thead>
            <tr style="background:#f1f5fa;">
              <th style="padding:8px 10px;text-align:left;color:#4a5a6a;font-size:12px;">#</th>
              <th style="padding:8px 10px;text-align:left;color:#4a5a6a;font-size:12px;">{texts['category']}</th>
              <th style="padding:8px 10px;text-align:right;color:#4a5a6a;font-size:12px;">{texts['amount']}</th>
            </tr>
          </thead>
          <tbody>
            {category_rows_html}
          </tbody>
        </table>
        {top_expenses_section}
        {footer_link_block}
      </div>
    </div>
  </body>
</html>
"""


def render_report_html(template_version="v1", **kwargs):
    # Phase 1: v1 is default and only available template.
    version = (template_version or "v1").strip().lower()
    if version != "v1":
        version = "v1"
    return render_report_html_v1(**kwargs)

