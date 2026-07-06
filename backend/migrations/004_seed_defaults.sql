INSERT INTO settings (key, value)
VALUES ('initial_saving', 0)
ON CONFLICT (key) DO NOTHING;

INSERT INTO settings (key, value)
VALUES ('per_page', 15)
ON CONFLICT (key) DO NOTHING;

INSERT INTO settings (key, value)
VALUES ('records_years', 1)
ON CONFLICT (key) DO NOTHING;

INSERT INTO settings (key, value)
VALUES (
    'app_initialized',
    CASE WHEN EXISTS (SELECT 1 FROM users) THEN 1 ELSE 0 END
)
ON CONFLICT (key) DO NOTHING;

INSERT INTO backup_config (id, frequency, weekly_day, retain_count)
VALUES (1, 'daily', 0, 7)
ON CONFLICT (id) DO NOTHING;

INSERT INTO smtp_settings (id, port, use_tls, enabled, updated_at)
VALUES (1, 587, TRUE, FALSE, NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO email_report_config (id, monthly_enabled, yearly_enabled, monthly_template_version, yearly_template_version, updated_at)
VALUES (1, TRUE, TRUE, 'v1', 'v1', NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO categories (name, description)
VALUES
    ('Basic Expenses', 'Rent or mortgage, community fees, utilities (electricity, water, internet/mobile, gas), life and home insurance'),
    ('Home', 'Home improvements and household purchases'),
    ('Food', 'Groceries, cafés and snacks'),
    ('Leisure', 'Going out, trips, cinema, concerts'),
    ('Transport', 'Car insurance, maintenance, fuel, public transport card'),
    ('Vacations', 'Travel, lodging, and holiday expenses'),
    ('Personal', 'Clothing, shoes, hairdresser, barber'),
    ('Sports', 'Gym, yoga, swimming'),
    ('Health', 'Health insurance, medicines'),
    ('Subscriptions', 'Netflix, iCloud, Spotify, Amazon Prime')
ON CONFLICT (name) DO NOTHING;
