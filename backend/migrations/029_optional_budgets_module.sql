INSERT INTO settings (key, value)
VALUES ('budgets_enabled', 1)
ON CONFLICT (key) DO NOTHING;
