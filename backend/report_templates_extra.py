from i18n import format_money


def _rows(items, empty_text, lang, accent):
    if not items:
        return f"<tr><td colspan='2' style='padding:12px;color:#718096'>{empty_text}</td></tr>"
    return "".join(
        f"<tr><td style='padding:8px 0;border-bottom:1px solid #e7e9ee'>{row[0]}</td>"
        f"<td style='padding:8px 0;border-bottom:1px solid #e7e9ee;text-align:right;color:{accent};font-weight:700'>"
        f"{format_money(float(row[1] or 0), lang)}</td></tr>"
        for row in items
    )


def render_report_html_v4(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#111827")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#111827")
    top_section = ""
    if include_top_expenses:
        top_section = f"""
        <div style="margin-top:28px;font:700 13px Georgia,serif;letter-spacing:.08em;text-transform:uppercase">{texts['top_expenses']}</div>
        <table width="100%" style="border-collapse:collapse;font-size:13px">{expense_rows}</table>"""
    return f"""<html data-finance-template="v4"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:24px;background:#f4f1eb;color:#111827;font-family:Arial,sans-serif">
<div style="max-width:720px;margin:auto;background:#fff;padding:36px;border-top:7px solid #111827">
  <h1 style="font:700 30px Georgia,serif;margin:8px 0 28px">{title}</h1>
  <table width="100%" style="border-collapse:collapse;border-top:1px solid #111827;border-bottom:1px solid #111827">
    <tr>
      <td style="padding:16px 4px"><small>{texts['income']}</small><br><b>{format_money(income, lang)}</b></td>
      <td style="padding:16px 4px"><small>{texts['expense']}</small><br><b>{format_money(expense, lang)}</b></td>
      <td style="padding:16px 4px"><small>{texts['saving']}</small><br><b>{format_money(saving, lang)}</b></td>
      <td style="padding:16px 4px;text-align:right"><small>{texts['balance']}</small><br><b>{format_money(balance, lang)}</b></td>
    </tr>
  </table>
  <div style="margin-top:28px;font:700 13px Georgia,serif;letter-spacing:.08em;text-transform:uppercase">{texts['category_summary']}</div>
  <table width="100%" style="border-collapse:collapse;font-size:13px">{category_rows}</table>
  {top_section}
  <!-- FINANCE_FOOTER_SLOT -->
</div></body></html>"""


def render_report_html_v5(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#7c3aed")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#7c3aed")
    top_section = ""
    if include_top_expenses:
        top_section = f"""<td width="50%" valign="top" style="padding:18px;background:#fff;border-radius:12px">
        <b>{texts['top_expenses']}</b><table width="100%" style="border-collapse:collapse;font-size:12px">{expense_rows}</table></td>"""
    cards = [
        (texts["income"], income, "#d1fae5", "#047857"),
        (texts["expense"], expense, "#fee2e2", "#b91c1c"),
        (texts["saving"], saving, "#fef3c7", "#a16207"),
        (texts["balance"], balance, "#ede9fe", "#6d28d9"),
    ]
    cards_html = "".join(
        f"<td width='25%' style='padding:12px;background:{bg};color:{fg};border-right:7px solid #f3f4f6'>"
        f"<small>{label}</small><br><b style='font-size:17px'>{format_money(value, lang)}</b></td>"
        for label, value, bg, fg in cards
    )
    return f"""<html data-finance-template="v5"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px;background:#111827;font-family:Arial,sans-serif;color:#1f2937">
<div style="max-width:760px;margin:auto">
  <div style="padding:24px;color:#fff;background:#7c3aed;border-radius:16px 16px 0 0">
    <div style="font-size:24px;font-weight:800;margin-top:5px">{title}</div>
  </div>
  <div style="padding:16px;background:#f3f4f6">
    <table width="100%" cellpadding="0" cellspacing="0"><tr>{cards_html}</tr></table>
    <table width="100%" cellpadding="0" cellspacing="8" style="margin-top:8px"><tr>
      <td width="50%" valign="top" style="padding:18px;background:#fff;border-radius:12px">
        <b>{texts['category_summary']}</b><table width="100%" style="border-collapse:collapse;font-size:12px">{category_rows}</table>
      </td>{top_section}
    </tr></table>
  </div>
  <!-- FINANCE_FOOTER_SLOT -->
</div></body></html>"""


def render_report_html_v6(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#111111")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#111111")
    detail = ""
    if include_top_expenses:
        detail = f"""<div style="margin:24px 0 6px">------------ {texts['top_expenses'].upper()} ------------</div>
        <table width="100%" style="border-collapse:collapse;font:12px 'Courier New',monospace">{expense_rows}</table>"""
    return f"""<html data-finance-template="v6"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px;background:#d9d9d9;font-family:'Courier New',monospace;color:#111">
<div style="max-width:520px;margin:auto;background:#fff;padding:28px;box-shadow:0 3px 16px #999">
  <div style="text-align:center;font-weight:bold;font-size:20px">*** FINANCE ***</div>
  <div style="text-align:center;margin:8px 0 22px">{title}</div>
  <div>------------------------------------------</div>
  <table width="100%" style="font:14px 'Courier New',monospace">
    <tr><td>{texts['income']}</td><td align="right">{format_money(income, lang)}</td></tr>
    <tr><td>{texts['expense']}</td><td align="right">{format_money(expense, lang)}</td></tr>
    <tr><td>{texts['saving']}</td><td align="right">{format_money(saving, lang)}</td></tr>
    <tr><td><b>{texts['balance']}</b></td><td align="right"><b>{format_money(balance, lang)}</b></td></tr>
  </table>
  <div>------------------------------------------</div>
  <div style="margin:24px 0 6px">--------- {texts['category_summary'].upper()} ---------</div>
  <table width="100%" style="border-collapse:collapse;font:12px 'Courier New',monospace">{category_rows}</table>
  {detail}
  <div style="text-align:center;margin-top:28px">********** END **********</div>
  <!-- FINANCE_FOOTER_SLOT -->
</div></body></html>"""


def render_report_html_v7(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#164e63")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#164e63")
    detail = ""
    if include_top_expenses:
        detail = f"""<div style="margin-top:24px;padding:18px;border:1px solid #cbd5e1">
        <b>{texts['top_expenses']}</b><table width="100%" style="border-collapse:collapse;font-size:12px">{expense_rows}</table></div>"""
    return f"""<html data-finance-template="v7"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:22px;background:#ecfeff;font-family:Arial,sans-serif;color:#164e63">
<table width="100%" style="max-width:760px;margin:auto;border-collapse:collapse;background:#fff">
 <tr>
  <td width="190" valign="top" style="padding:28px;background:#164e63;color:#fff">
    <div style="font-size:12px">{texts['balance']}</div>
    <div style="font-size:22px;font-weight:800">{format_money(balance, lang)}</div>
  </td>
  <td valign="top" style="padding:28px">
    <h1 style="font-size:22px;margin:0 0 22px">{title}</h1>
    <table width="100%" style="border-collapse:collapse;background:#f0fdfa">
      <tr><td style="padding:12px">{texts['income']}<br><b>{format_money(income, lang)}</b></td>
      <td style="padding:12px">{texts['expense']}<br><b>{format_money(expense, lang)}</b></td>
      <td style="padding:12px">{texts['saving']}<br><b>{format_money(saving, lang)}</b></td></tr>
    </table>
    <div style="margin-top:24px;padding:18px;border:1px solid #cbd5e1">
      <b>{texts['category_summary']}</b><table width="100%" style="border-collapse:collapse;font-size:12px">{category_rows}</table>
    </div>
    {detail}
    <!-- FINANCE_FOOTER_SLOT -->
  </td>
 </tr>
</table></body></html>"""


def render_report_html_v8(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#e11d48")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#e11d48")
    detail = ""
    if include_top_expenses:
        detail = f"""<div style="padding:20px;background:#fff1f2;border-radius:18px">
        <div style="font-size:18px;font-weight:800">{texts['top_expenses']}</div>
        <table width="100%" style="border-collapse:collapse;font-size:12px">{expense_rows}</table></div>"""
    return f"""<html data-finance-template="v8"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:24px;background:#fff7ed;font-family:Arial,sans-serif;color:#431407">
<div style="max-width:760px;margin:auto">
  <div style="padding:30px;background:#fb7185;border-radius:28px 28px 8px 8px;color:#fff">
    <div style="font-size:34px;font-weight:900;line-height:1;margin-top:8px">{title}</div>
  </div>
  <table width="100%" cellspacing="8" style="margin:10px -8px">
    <tr>
      <td style="padding:18px;background:#fed7aa;border-radius:18px">{texts['income']}<br><b style="font-size:20px">{format_money(income, lang)}</b></td>
      <td style="padding:18px;background:#fecdd3;border-radius:18px">{texts['expense']}<br><b style="font-size:20px">{format_money(expense, lang)}</b></td>
    </tr><tr>
      <td style="padding:18px;background:#fde68a;border-radius:18px">{texts['saving']}<br><b style="font-size:20px">{format_money(saving, lang)}</b></td>
      <td style="padding:18px;background:#fbcfe8;border-radius:18px">{texts['balance']}<br><b style="font-size:20px">{format_money(balance, lang)}</b></td>
    </tr>
  </table>
  <div style="padding:20px;background:#fff;border-radius:18px;margin-bottom:10px">
    <div style="font-size:18px;font-weight:800">{texts['category_summary']}</div>
    <table width="100%" style="border-collapse:collapse;font-size:12px">{category_rows}</table>
  </div>
  {detail}
  <!-- FINANCE_FOOTER_SLOT -->
</div></body></html>"""


def render_report_html_v9(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#2563eb")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#2563eb")
    top_section = (
        f"<div style='margin-top:24px'><div style='font-size:11px;letter-spacing:.18em;color:#64748b'>{texts['top_expenses'].upper()}</div>"
        f"<table width='100%' style='border-collapse:collapse;font-size:12px'>{expense_rows}</table></div>"
        if include_top_expenses else ""
    )
    return f"""<html data-finance-template="v9"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:28px;background:#f8fafc;font-family:Arial,sans-serif;color:#0f172a">
<div style="max-width:720px;margin:auto;background:#fff;border:1px solid #e2e8f0;padding:34px">
  <h1 style="font-size:27px;line-height:1.15;margin:14px 0 28px">{title}</h1>
  <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse">
    <tr>
      <td style="padding:16px 0;border-top:1px solid #e2e8f0"><small style="color:#64748b">{texts['income']}</small><br><b>{format_money(income, lang)}</b></td>
      <td style="padding:16px 0;border-top:1px solid #e2e8f0"><small style="color:#64748b">{texts['expense']}</small><br><b>{format_money(expense, lang)}</b></td>
      <td style="padding:16px 0;border-top:1px solid #e2e8f0"><small style="color:#64748b">{texts['saving']}</small><br><b>{format_money(saving, lang)}</b></td>
      <td style="padding:16px 0;border-top:1px solid #e2e8f0;text-align:right"><small style="color:#64748b">{texts['balance']}</small><br><b style="color:#2563eb">{format_money(balance, lang)}</b></td>
    </tr>
  </table>
  <div style="margin-top:24px"><div style="font-size:11px;letter-spacing:.18em;color:#64748b">{texts['category_summary'].upper()}</div>
  <table width="100%" style="border-collapse:collapse;font-size:12px">{category_rows}</table></div>
  {top_section}
  <!-- FINANCE_FOOTER_SLOT -->
</div></body></html>"""


def render_report_html_v10(
    title, period_label, income, expense, saving, balance, top_expenses,
    category_summary, texts, include_top_expenses=True, lang="en",
):
    category_rows = _rows(category_summary, texts["no_category_data"], lang, "#22d3ee")
    expense_rows = _rows(top_expenses, texts["no_expense_data"], lang, "#f472b6")
    top_section = (
        f"<div style='margin-top:14px;padding:18px;background:#111827;border:1px solid #334155;border-radius:12px'>"
        f"<b style='color:#f472b6'>{texts['top_expenses']}</b><table width='100%' style='border-collapse:collapse;font-size:12px;color:#e2e8f0'>{expense_rows}</table></div>"
        if include_top_expenses else ""
    )
    return f"""<html data-finance-template="v10"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:24px;background:#020617;font-family:Arial,sans-serif;color:#e2e8f0">
<div style="max-width:760px;margin:auto;background:#0f172a;border:1px solid #334155;border-radius:18px;overflow:hidden">
  <div style="padding:26px;background:linear-gradient(135deg,#0e7490,#7e22ce)">
    <div style="font-size:29px;font-weight:900;margin-top:8px;color:#fff">{title}</div>
  </div>
  <div style="padding:20px">
    <table width="100%" cellspacing="7"><tr>
      <td style="padding:15px;background:#082f49;border-radius:10px">{texts['income']}<br><b style="color:#67e8f9">{format_money(income, lang)}</b></td>
      <td style="padding:15px;background:#4c0519;border-radius:10px">{texts['expense']}<br><b style="color:#fda4af">{format_money(expense, lang)}</b></td>
      <td style="padding:15px;background:#422006;border-radius:10px">{texts['saving']}<br><b style="color:#fcd34d">{format_money(saving, lang)}</b></td>
      <td style="padding:15px;background:#2e1065;border-radius:10px">{texts['balance']}<br><b style="color:#d8b4fe">{format_money(balance, lang)}</b></td>
    </tr></table>
    <div style="margin-top:14px;padding:18px;background:#111827;border:1px solid #334155;border-radius:12px">
      <b style="color:#22d3ee">{texts['category_summary']}</b><table width="100%" style="border-collapse:collapse;font-size:12px;color:#e2e8f0">{category_rows}</table>
    </div>
    {top_section}
    <!-- FINANCE_FOOTER_SLOT -->
  </div>
</div></body></html>"""
