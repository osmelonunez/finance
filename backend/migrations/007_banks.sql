CREATE TABLE IF NOT EXISTS banks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE payment_methods
ADD COLUMN IF NOT EXISTS bank_id INTEGER REFERENCES banks(id) ON DELETE RESTRICT;

ALTER TABLE loans
ADD COLUMN IF NOT EXISTS bank_id INTEGER REFERENCES banks(id) ON DELETE RESTRICT;

CREATE INDEX IF NOT EXISTS idx_banks_active ON banks(is_active);
CREATE INDEX IF NOT EXISTS idx_payment_methods_bank_id ON payment_methods(bank_id);
CREATE INDEX IF NOT EXISTS idx_loans_bank_id ON loans(bank_id);
