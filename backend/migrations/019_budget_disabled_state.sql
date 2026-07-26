ALTER TABLE category_budgets
    ADD COLUMN IF NOT EXISTS is_disabled BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE category_budgets
    ALTER COLUMN amount DROP NOT NULL;

ALTER TABLE category_budgets
    DROP CONSTRAINT IF EXISTS category_budgets_amount_check;

ALTER TABLE category_budgets
    DROP CONSTRAINT IF EXISTS category_budgets_state_chk;

ALTER TABLE category_budgets
    ADD CONSTRAINT category_budgets_state_chk
    CHECK (
        (is_disabled = TRUE AND amount IS NULL)
        OR
        (is_disabled = FALSE AND amount IS NOT NULL AND amount > 0)
    );

