ALTER TABLE records
    DROP CONSTRAINT IF EXISTS records_is_financed_expense_chk;

ALTER TABLE records
    DROP COLUMN IF EXISTS is_financed;
