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
