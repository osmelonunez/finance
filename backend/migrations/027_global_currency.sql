ALTER TABLE settings
    ADD COLUMN IF NOT EXISTS text_value TEXT;

INSERT INTO settings (key, value, text_value)
VALUES ('currency', 0, 'EUR')
ON CONFLICT (key) DO NOTHING;
