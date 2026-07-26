ALTER TABLE payment_methods
    ADD COLUMN IF NOT EXISTS account_type TEXT,
    ADD COLUMN IF NOT EXISTS initial_balance NUMERIC(12,2) NOT NULL DEFAULT 0;

UPDATE payment_methods
SET account_type = 'current'
WHERE kind = 'bank_account'
  AND account_type IS NULL;

ALTER TABLE payment_methods
    DROP CONSTRAINT IF EXISTS payment_methods_account_type_chk;

ALTER TABLE payment_methods
    ADD CONSTRAINT payment_methods_account_type_chk
    CHECK (
        (
            kind = 'bank_account'
            AND COALESCE(account_type, 'current') IN ('current', 'savings')
            AND initial_balance >= 0
        )
        OR
        (
            kind = 'card'
            AND account_type IS NULL
            AND initial_balance = 0
        )
    );

ALTER TABLE records
    DROP CONSTRAINT IF EXISTS records_payment_method_expense_chk;

ALTER TABLE records
    ADD CONSTRAINT records_payment_method_type_chk
    CHECK (payment_method_id IS NULL OR type IN ('expense', 'saving'));

CREATE INDEX IF NOT EXISTS idx_payment_methods_account_type
ON payment_methods(account_type);
