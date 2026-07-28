ALTER TABLE backup_config
    ADD COLUMN IF NOT EXISTS retain_days INTEGER NOT NULL DEFAULT 7;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'backup_config' AND column_name = 'retain_count'
    ) THEN
        EXECUTE 'UPDATE backup_config SET retain_days = COALESCE(retain_count, retain_days, 7)';
    END IF;
END $$;

ALTER TABLE backup_config
    DROP COLUMN IF EXISTS retain_count;

ALTER TABLE backup_runs
    ADD COLUMN IF NOT EXISTS checksum_sha256 TEXT;
