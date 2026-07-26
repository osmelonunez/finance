CREATE TABLE IF NOT EXISTS category_budgets (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    month VARCHAR(7) NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    created_by TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_by TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT category_budgets_month_chk
        CHECK (month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'),
    CONSTRAINT uq_category_budgets_category_month UNIQUE (category_id, month)
);

CREATE INDEX IF NOT EXISTS idx_category_budgets_month
ON category_budgets(month);

