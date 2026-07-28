ALTER TABLE backup_config
    ADD COLUMN IF NOT EXISTS retain_days INTEGER NOT NULL DEFAULT 7,
    DROP COLUMN IF EXISTS retain_daily,
    DROP COLUMN IF EXISTS retain_weekly,
    DROP COLUMN IF EXISTS retain_monthly;
