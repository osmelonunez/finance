CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    bank_name TEXT NOT NULL,
    principal_amount NUMERIC(10,2) NOT NULL CHECK (principal_amount > 0),
    term_months INTEGER NOT NULL CHECK (term_months > 0),
    monthly_payment NUMERIC(10,2) CHECK (monthly_payment IS NULL OR monthly_payment > 0),
    start_date VARCHAR(7) NOT NULL,
    description TEXT,
    exclude_from_dashboard BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paid', 'cancelled')),
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by TEXT
);

ALTER TABLE records
ADD COLUMN IF NOT EXISTS loan_id INTEGER REFERENCES loans(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS is_loan_payment BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_loans_bank_name ON loans(bank_name);
CREATE INDEX IF NOT EXISTS idx_loans_dashboard_visibility ON loans(exclude_from_dashboard);
CREATE INDEX IF NOT EXISTS idx_records_loan_id ON records(loan_id);
CREATE INDEX IF NOT EXISTS idx_records_loan_payment ON records(is_loan_payment);

ALTER TABLE records
DROP CONSTRAINT IF EXISTS records_loan_payment_expense_chk;

ALTER TABLE records
ADD CONSTRAINT records_loan_payment_expense_chk
    CHECK (NOT is_loan_payment OR (type = 'expense' AND loan_id IS NOT NULL));
