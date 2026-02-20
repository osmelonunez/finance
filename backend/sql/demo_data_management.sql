-- Demo dataset helpers for Management page
-- Usage:
--   SELECT management_seed_demo_data();
--   SELECT management_clear_demo_data();
--
-- Dataset scope:
-- - 5 years: current year, 2 previous, 2 next (all months)
-- - Previous years: lower income + lower expenses
-- - Future years: higher income + higher expenses
-- - Savings: higher in previous years, lower in future years

CREATE OR REPLACE FUNCTION management_seed_demo_data()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    demo_tag TEXT := '[DEMO_SEED_MANAGEMENT]';
    actor_username TEXT;
    inserted_count INTEGER;
BEGIN
    DELETE FROM records WHERE comment = demo_tag;

    INSERT INTO settings (key, value)
    VALUES ('initial_saving', 300)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

    INSERT INTO payment_methods (name, kind, bank_name, account_ref, is_active, updated_at)
    VALUES
        ('Demo - Main Card', 'card', 'ING', '**** 1234', TRUE, NOW()),
        ('Demo - Shared Card', 'card', 'Santander', '**** 9876', TRUE, NOW()),
        ('Demo - Current Account', 'bank_account', 'ING', 'ES91 0000 0000 0000 0000', TRUE, NOW())
    ON CONFLICT (name) DO UPDATE
    SET
        kind = EXCLUDED.kind,
        bank_name = EXCLUDED.bank_name,
        account_ref = EXCLUDED.account_ref,
        is_active = EXCLUDED.is_active,
        updated_at = NOW();

    SELECT username
    INTO actor_username
    FROM users
    WHERE is_admin = TRUE
    ORDER BY id
    LIMIT 1;

    IF actor_username IS NULL OR actor_username = '' THEN
        actor_username := 'admin';
    END IF;

    WITH calendar AS (
        SELECT
            d::date AS month_date,
            EXTRACT(YEAR FROM d)::int AS year_num,
            TO_CHAR(d, 'YYYY-MM') AS ym
        FROM GENERATE_SERIES(
            MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int - 2, 1, 1),
            MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int + 2, 12, 1),
            INTERVAL '1 month'
        ) AS d
    ),
    factors AS (
        SELECT
            c.ym,
            c.year_num,
            CASE (c.year_num - EXTRACT(YEAR FROM CURRENT_DATE)::int)
                WHEN -2 THEN 0.82
                WHEN -1 THEN 0.90
                WHEN  0 THEN 1.00
                WHEN  1 THEN 1.10
                WHEN  2 THEN 1.20
                ELSE 1.00
            END AS income_mult,
            CASE (c.year_num - EXTRACT(YEAR FROM CURRENT_DATE)::int)
                WHEN -2 THEN 0.80
                WHEN -1 THEN 0.90
                WHEN  0 THEN 1.00
                WHEN  1 THEN 1.12
                WHEN  2 THEN 1.25
                ELSE 1.00
            END AS expense_mult,
            CASE (c.year_num - EXTRACT(YEAR FROM CURRENT_DATE)::int)
                WHEN -2 THEN 1.40
                WHEN -1 THEN 1.25
                WHEN  0 THEN 1.00
                WHEN  1 THEN 0.85
                WHEN  2 THEN 0.70
                ELSE 1.00
            END AS saving_mult
        FROM calendar c
    ),
    demo_rows AS (
        SELECT
            v.concept,
            ROUND((
                CASE
                    WHEN v.type = 'income' THEN v.base_amount * f.income_mult
                    WHEN v.type = 'expense' THEN v.base_amount * f.expense_mult
                    ELSE v.base_amount * f.saving_mult
                END
            )::numeric, 2) AS amount,
            f.ym AS date,
            v.type,
            v.source,
            demo_tag AS comment,
            c.id AS category_id,
            pm.id AS payment_method_id,
            v.is_financed,
            v.deferred_total,
            actor_username AS created_by,
            NOW() AS created_at,
            NOW() AS updated_at,
            actor_username AS updated_by
        FROM factors f
        CROSS JOIN LATERAL (
            VALUES
                ('Payroll - Main Job',       1600.00, 'income',  NULL::TEXT,     NULL::TEXT,      NULL::TEXT,                 FALSE, NULL::INT),
                ('Payroll - Secondary Job',  2000.00, 'income',  NULL::TEXT,     NULL::TEXT,      NULL::TEXT,                 FALSE, NULL::INT),
                ('Monthly Saving',            500.00, 'saving',  NULL::TEXT,     NULL::TEXT,      NULL::TEXT,                 FALSE, NULL::INT),
                ('Rent / Mortgage',           900.00, 'expense', 'monthly',      'Basic Expenses', 'Demo - Current Account',   FALSE, NULL::INT),
                ('Utilities',                 140.00, 'expense', 'monthly',      'Basic Expenses', 'Demo - Current Account',   FALSE, NULL::INT),
                ('Groceries',                 330.00, 'expense', 'monthly',      'Food',           'Demo - Shared Card',       TRUE,  NULL::INT),
                ('Transport',                  95.00, 'expense', 'monthly',      'Transport',      'Demo - Main Card',         TRUE,  NULL::INT),
                ('Gym',                        40.00, 'expense', 'monthly',      'Sports',         'Demo - Main Card',         TRUE,  NULL::INT),
                ('Streaming subscriptions',    22.00, 'expense', 'monthly',      'Subscriptions',  'Demo - Shared Card',       TRUE,  NULL::INT),
                ('Leisure activities',        120.00, 'expense', 'monthly',      'Leisure',        'Demo - Main Card',         TRUE,  NULL::INT),
                ('Laptop installment',        180.00, 'expense', 'monthly',      'Home',           'Demo - Main Card',         TRUE,  3)
        ) AS v(concept, base_amount, type, source, category_name, payment_method_name, is_financed, deferred_total)
        LEFT JOIN categories c ON c.name = v.category_name
        LEFT JOIN payment_methods pm ON pm.name = v.payment_method_name
    ),
    demo_rows_expanded AS (
        SELECT
            d.concept,
            d.amount,
            CASE
                WHEN d.type = 'expense' AND COALESCE(d.deferred_total, 1) > 1
                    THEN TO_CHAR((TO_DATE(d.date || '-01', 'YYYY-MM-DD') + ((inst.idx - 1) || ' month')::interval), 'YYYY-MM')
                ELSE d.date
            END AS date,
            d.type,
            d.source,
            d.comment,
            d.category_id,
            d.payment_method_id,
            d.is_financed,
            CASE
                WHEN d.type = 'expense' AND COALESCE(d.deferred_total, 1) > 1 THEN inst.idx
                ELSE NULL
            END AS deferred_index,
            CASE
                WHEN d.type = 'expense' AND COALESCE(d.deferred_total, 1) > 1 THEN d.deferred_total
                ELSE NULL
            END AS deferred_total,
            d.created_by,
            d.created_at,
            d.updated_at,
            d.updated_by
        FROM demo_rows d
        CROSS JOIN LATERAL generate_series(
            1,
            CASE
                WHEN d.type = 'expense' AND COALESCE(d.deferred_total, 1) > 1 THEN d.deferred_total
                ELSE 1
            END
        ) AS inst(idx)
    ),
    inserted AS (
        INSERT INTO records (
            concept, amount, date, type, source, comment, category_id, payment_method_id, is_financed,
            deferred_index, deferred_total, created_by, created_at, updated_at, updated_by
        )
        SELECT
            concept, amount, date, type, source, comment, category_id, payment_method_id, is_financed,
            deferred_index, deferred_total, created_by, created_at, updated_at, updated_by
        FROM demo_rows_expanded
        RETURNING 1
    )
    SELECT COUNT(*) INTO inserted_count FROM inserted;

    RETURN inserted_count;
END;
$$;


CREATE OR REPLACE FUNCTION management_clear_demo_data()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM records
    WHERE comment = '[DEMO_SEED_MANAGEMENT]';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    DELETE FROM settings WHERE key = 'initial_saving';
    DELETE FROM payment_methods pm
    WHERE pm.name IN ('Demo - Main Card', 'Demo - Shared Card', 'Demo - Current Account')
      AND NOT EXISTS (SELECT 1 FROM records r WHERE r.payment_method_id = pm.id);
    RETURN deleted_count;
END;
$$;
