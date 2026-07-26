DROP INDEX IF EXISTS idx_records_type_source_date;

ALTER TABLE records
    DROP COLUMN IF EXISTS source;

CREATE INDEX IF NOT EXISTS idx_records_type_date
    ON records(type, date);
