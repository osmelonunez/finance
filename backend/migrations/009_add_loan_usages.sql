CREATE TABLE IF NOT EXISTS loan_usages (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    concept TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    date VARCHAR(7) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    comment TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_loan_usages_loan_id ON loan_usages(loan_id);
CREATE INDEX IF NOT EXISTS idx_loan_usages_date ON loan_usages(date);
CREATE INDEX IF NOT EXISTS idx_loan_usages_category_id ON loan_usages(category_id);
