ALTER TABLE email_report_config
    ADD COLUMN IF NOT EXISTS brand_name TEXT NOT NULL DEFAULT 'Finance',
    ADD COLUMN IF NOT EXISTS header_text TEXT NOT NULL DEFAULT 'Personal finance report',
    ADD COLUMN IF NOT EXISTS footer_text TEXT NOT NULL DEFAULT '© {year} Osmel Nuñez Alonso · v{version} · GitHub';
