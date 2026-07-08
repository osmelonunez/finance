ALTER TABLE loans
DROP CONSTRAINT IF EXISTS loans_annual_interest_rate_check;

ALTER TABLE loans
ALTER COLUMN annual_interest_rate TYPE TEXT
USING NULLIF(annual_interest_rate::TEXT, '');
