CREATE TABLE IF NOT EXISTS email_report_config (
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    monthly_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    yearly_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    monthly_template_version TEXT NOT NULL DEFAULT 'v1',
    yearly_template_version TEXT NOT NULL DEFAULT 'v1',
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_report_runs (
    id SERIAL PRIMARY KEY,
    report_type TEXT NOT NULL CHECK (report_type IN ('monthly', 'yearly', 'test_monthly', 'test_yearly')),
    period_key TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'failed')),
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
