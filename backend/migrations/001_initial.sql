CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    language TEXT NOT NULL DEFAULT 'en',
    per_page INTEGER NOT NULL DEFAULT 15,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_lower
ON users (LOWER(email));

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username_lower
ON users (LOWER(username));

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('card', 'bank_account')),
    bank_name TEXT,
    account_ref TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    concept TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    date VARCHAR(7) NOT NULL,
    type VARCHAR(10) NOT NULL
        CHECK (type IN ('income','expense','saving')),
    source VARCHAR(10)
        CHECK (source IN ('monthly','saving')),
    comment TEXT,
    category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT,
    payment_method_id INTEGER REFERENCES payment_methods(id) ON DELETE RESTRICT,
    is_financed BOOLEAN NOT NULL DEFAULT FALSE,
    deferred_index INTEGER,
    deferred_total INTEGER,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by TEXT,
    CONSTRAINT records_payment_method_expense_chk
        CHECK (payment_method_id IS NULL OR type='expense'),
    CONSTRAINT records_is_financed_expense_chk
        CHECK (NOT is_financed OR type='expense'),
    CONSTRAINT records_deferred_values_chk
        CHECK (
            (deferred_index IS NULL AND deferred_total IS NULL)
            OR
            (
                deferred_index IS NOT NULL
                AND deferred_total IS NOT NULL
                AND deferred_index >= 1
                AND deferred_total >= 2
                AND deferred_index <= deferred_total
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_payment_methods_kind ON payment_methods(kind);
CREATE INDEX IF NOT EXISTS idx_payment_methods_active ON payment_methods(is_active);
CREATE INDEX IF NOT EXISTS idx_records_category_id ON records(category_id);
CREATE INDEX IF NOT EXISTS idx_records_payment_method_id ON records(payment_method_id);
CREATE INDEX IF NOT EXISTS idx_records_type_date ON records(type, date);
CREATE INDEX IF NOT EXISTS idx_records_type_source_date ON records(type, source, date);
CREATE INDEX IF NOT EXISTS idx_records_category_date ON records(category_id, date);
CREATE INDEX IF NOT EXISTS idx_records_payment_method_date ON records(payment_method_id, date);

CREATE TABLE IF NOT EXISTS backup_config (
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    frequency TEXT NOT NULL DEFAULT 'daily'
        CHECK (frequency IN ('daily', 'weekly', 'monthly_last_day')),
    weekly_day SMALLINT NOT NULL DEFAULT 0
        CHECK (weekly_day BETWEEN 0 AND 6),
    retain_count INTEGER NOT NULL DEFAULT 7
        CHECK (retain_count BETWEEN 1 AND 365),
    last_run_at TIMESTAMP NULL,
    last_cleanup_at TIMESTAMP NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS backup_runs (
    id SERIAL PRIMARY KEY,
    trigger TEXT NOT NULL DEFAULT 'manual',
    filename TEXT,
    file_path TEXT,
    size_bytes BIGINT,
    status TEXT NOT NULL
        CHECK (status IN ('success', 'failed')),
    message TEXT,
    created_by TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS smtp_settings (
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    host TEXT,
    port INTEGER NOT NULL DEFAULT 587,
    username TEXT,
    password_encrypted TEXT,
    from_name TEXT,
    from_email TEXT,
    use_tls BOOLEAN NOT NULL DEFAULT TRUE,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

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
