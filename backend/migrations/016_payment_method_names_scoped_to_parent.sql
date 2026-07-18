ALTER TABLE payment_methods
DROP CONSTRAINT IF EXISTS payment_methods_name_key;

CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_methods_account_name_bank
ON payment_methods(bank_id, name)
WHERE kind = 'bank_account';

CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_methods_card_name_account
ON payment_methods(parent_account_id, name)
WHERE kind = 'card' AND parent_account_id IS NOT NULL;
