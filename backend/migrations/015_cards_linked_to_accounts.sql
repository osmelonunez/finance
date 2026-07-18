ALTER TABLE payment_methods
ADD COLUMN IF NOT EXISTS parent_account_id INTEGER REFERENCES payment_methods(id) ON DELETE RESTRICT;

CREATE INDEX IF NOT EXISTS idx_payment_methods_parent_account_id
ON payment_methods(parent_account_id);
