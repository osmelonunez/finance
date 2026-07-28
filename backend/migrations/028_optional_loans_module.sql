INSERT INTO settings (key, value)
VALUES ('loans_enabled', 1)
ON CONFLICT (key) DO NOTHING;
