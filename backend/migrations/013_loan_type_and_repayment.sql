ALTER TABLE loans
ADD COLUMN IF NOT EXISTS loan_type TEXT NOT NULL DEFAULT 'standard',
ADD COLUMN IF NOT EXISTS total_repayment_amount NUMERIC(10,2)
    CHECK (total_repayment_amount IS NULL OR total_repayment_amount > 0);

UPDATE loans
SET loan_type = CASE
    WHEN is_mortgage THEN 'mortgage'
    WHEN annual_interest_rate IS NOT NULL THEN 'interest'
    ELSE 'standard'
END
WHERE loan_type IS NULL OR loan_type = 'standard';

ALTER TABLE loans
DROP CONSTRAINT IF EXISTS loans_loan_type_chk;

ALTER TABLE loans
ADD CONSTRAINT loans_loan_type_chk
    CHECK (loan_type IN ('standard', 'interest', 'mortgage'));

CREATE INDEX IF NOT EXISTS idx_loans_loan_type ON loans(loan_type);
