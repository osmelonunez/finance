ALTER TABLE loans
ADD COLUMN IF NOT EXISTS is_mortgage BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS annual_interest_rate NUMERIC(6,3)
    CHECK (annual_interest_rate IS NULL OR annual_interest_rate >= 0),
ADD COLUMN IF NOT EXISTS monthly_principal_amount NUMERIC(10,2)
    CHECK (monthly_principal_amount IS NULL OR monthly_principal_amount > 0),
ADD COLUMN IF NOT EXISTS monthly_interest_amount NUMERIC(10,2)
    CHECK (monthly_interest_amount IS NULL OR monthly_interest_amount >= 0);

ALTER TABLE records
ADD COLUMN IF NOT EXISTS loan_principal_amount NUMERIC(10,2),
ADD COLUMN IF NOT EXISTS loan_interest_amount NUMERIC(10,2);

ALTER TABLE loans
DROP CONSTRAINT IF EXISTS loans_mortgage_monthly_split_chk;

ALTER TABLE loans
ADD CONSTRAINT loans_mortgage_monthly_split_chk
    CHECK (
        NOT is_mortgage
        OR monthly_payment IS NULL
        OR (
            monthly_principal_amount IS NOT NULL
            AND monthly_interest_amount IS NOT NULL
            AND monthly_principal_amount + monthly_interest_amount = monthly_payment
        )
    );

ALTER TABLE records
DROP CONSTRAINT IF EXISTS records_loan_payment_split_chk;

ALTER TABLE records
ADD CONSTRAINT records_loan_payment_split_chk
    CHECK (
        NOT is_loan_payment
        OR (
            loan_principal_amount IS NULL
            AND loan_interest_amount IS NULL
        )
        OR (
            loan_principal_amount IS NOT NULL
            AND loan_interest_amount IS NOT NULL
            AND loan_principal_amount > 0
            AND loan_interest_amount >= 0
            AND loan_principal_amount + loan_interest_amount = amount
        )
    );

CREATE INDEX IF NOT EXISTS idx_loans_is_mortgage ON loans(is_mortgage);
