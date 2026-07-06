-- Compound indexes for common records filters/sorting patterns.
-- Safe to run in existing databases thanks to IF NOT EXISTS.

CREATE INDEX IF NOT EXISTS idx_records_type_category_date
    ON records(type, category_id, date);

CREATE INDEX IF NOT EXISTS idx_records_type_payment_method_date
    ON records(type, payment_method_id, date);

CREATE INDEX IF NOT EXISTS idx_records_type_date_id_desc
    ON records(type, date DESC, id DESC);
