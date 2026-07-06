ALTER TABLE loans
ADD COLUMN IF NOT EXISTS exclude_from_dashboard BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_loans_dashboard_visibility
ON loans(exclude_from_dashboard);
