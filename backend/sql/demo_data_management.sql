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
-- - Current year loans: Universidad (60% paid), Reforma (80% paid), Coche (100% paid), plus a previous-year mortgage excluded from dashboard loan totals.

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

    INSERT INTO banks (name, is_active, updated_at)
    VALUES
        ('ING', TRUE, NOW()),
        ('Santander', TRUE, NOW()),
        ('CaixaBank', TRUE, NOW()),
        ('BBVA', TRUE, NOW())
    ON CONFLICT (name) DO UPDATE
    SET is_active = TRUE,
        updated_at = NOW();

    INSERT INTO payment_methods (name, kind, bank_id, bank_name, account_ref, is_active, updated_at)
    VALUES
        ('Demo - Main Card', 'card', (SELECT id FROM banks WHERE name='ING'), 'ING', '**** 1234', TRUE, NOW()),
        ('Demo - Shared Card', 'card', (SELECT id FROM banks WHERE name='Santander'), 'Santander', '**** 9876', TRUE, NOW()),
        ('Demo - Current Account', 'bank_account', (SELECT id FROM banks WHERE name='ING'), 'ING', 'ES91 0000 0000 0000 0000', TRUE, NOW())
    ON CONFLICT (name) DO UPDATE
    SET
        kind = EXCLUDED.kind,
        bank_id = EXCLUDED.bank_id,
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

    DELETE FROM loans WHERE description LIKE demo_tag || '%';

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
    demo_loans AS (
        INSERT INTO loans (
            name, bank_id, bank_name, principal_amount, term_months, monthly_payment,
            start_date, description, exclude_from_dashboard, status, created_by, created_at, updated_at, updated_by
        )
        VALUES
            (
                'Universidad',
                (SELECT id FROM banks WHERE name='CaixaBank'),
                'CaixaBank',
                8000.00,
                36,
                283.33,
                TO_CHAR(MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1), 'YYYY-MM'),
                demo_tag || ' Estudios universitarios y matricula',
                FALSE,
                'active',
                actor_username,
                NOW(),
                NOW(),
                actor_username
            ),
            (
                'Reforma',
                (SELECT id FROM banks WHERE name='BBVA'),
                'BBVA',
                5500.00,
                24,
                275.00,
                TO_CHAR(MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 3, 1), 'YYYY-MM'),
                demo_tag || ' Reforma parcial de vivienda',
                FALSE,
                'active',
                actor_username,
                NOW(),
                NOW(),
                actor_username
            ),
            (
                'Coche',
                (SELECT id FROM banks WHERE name='Santander'),
                'Santander',
                3600.00,
                12,
                300.00,
                TO_CHAR(MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1), 'YYYY-MM'),
                demo_tag || ' Compra de coche de segunda mano',
                FALSE,
                'paid',
                actor_username,
                NOW(),
                NOW(),
                actor_username
            ),
            (
                'Hipoteca vivienda',
                (SELECT id FROM banks WHERE name='ING'),
                'ING',
                210000.00,
                360,
                900.00,
                TO_CHAR(MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int - 1, 2, 1), 'YYYY-MM'),
                demo_tag || ' Hipoteca de vivienda principal',
                TRUE,
                'active',
                actor_username,
                NOW(),
                NOW(),
                actor_username
            )
        RETURNING id, name, principal_amount
    ),
    loan_payment_plan AS (
        SELECT
            dl.id AS loan_id,
            dl.name AS loan_name,
            lp.payment_method_name,
            lp.payment_count,
            lp.target_paid,
            gs.idx AS payment_index,
            TO_CHAR(
                lp.start_month + ((gs.idx - 1) || ' month')::interval,
                'YYYY-MM'
            ) AS date,
            CASE
                WHEN gs.idx = lp.payment_count
                    THEN lp.target_paid - ROUND((lp.target_paid / lp.payment_count)::numeric, 2) * (lp.payment_count - 1)
                ELSE ROUND((lp.target_paid / lp.payment_count)::numeric, 2)
            END AS amount
        FROM (
            VALUES
                (
                    'Universidad',
                    'Demo - Current Account',
                    MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1),
                    24,
                    4800.00::numeric
                ),
                (
                    'Reforma',
                    'Demo - Main Card',
                    MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 3, 1),
                    18,
                    4400.00::numeric
                ),
                (
                    'Coche',
                    'Demo - Shared Card',
                    MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1),
                    12,
                    3600.00::numeric
                ),
                (
                    'Hipoteca vivienda',
                    'Demo - Current Account',
                    MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int - 1, 2, 1),
                    EXTRACT(MONTH FROM CURRENT_DATE)::int + 11,
                    (900.00 * (EXTRACT(MONTH FROM CURRENT_DATE)::int + 11))::numeric
                )
        ) AS lp(loan_name, payment_method_name, start_month, payment_count, target_paid)
        JOIN demo_loans dl ON dl.name = lp.loan_name
        CROSS JOIN LATERAL generate_series(1, lp.payment_count) AS gs(idx)
    ),
    loan_usage_plan AS (
        SELECT
            dl.id AS loan_id,
            lu.concept,
            lu.amount,
            TO_CHAR(lu.usage_month, 'YYYY-MM') AS date,
            lu.category_name,
            lu.comment
        FROM (
            VALUES
                ('Universidad', 'Matricula universidad', 4200.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1), 'Personal', 'Primer pago de matricula'),
                ('Universidad', 'Material y libros', 900.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 2, 1), 'Personal', 'Libros y materiales del curso'),
                ('Reforma', 'Azulejos baño', 850.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 3, 1), 'Home', 'Material principal del baño'),
                ('Reforma', 'Mano de obra baño', 2200.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 4, 1), 'Home', 'Instalacion y reforma'),
                ('Reforma', 'Mueble y sanitarios', 950.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 5, 1), 'Home', 'Equipamiento final'),
                ('Coche', 'Compra coche segunda mano', 3400.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1), 'Transport', 'Pago principal del vehiculo'),
                ('Coche', 'Cambio de titularidad', 200.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int, 1, 1), 'Transport', 'Tramites iniciales'),
                ('Hipoteca vivienda', 'Compra vivienda principal', 210000.00::numeric, MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int - 1, 2, 1), 'Home', 'Importe financiado para la compra de vivienda')
        ) AS lu(loan_name, concept, amount, usage_month, category_name, comment)
        JOIN demo_loans dl ON dl.name = lu.loan_name
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
            v.deferred_total,
            actor_username AS created_by,
            NOW() AS created_at,
            NOW() AS updated_at,
            actor_username AS updated_by
        FROM factors f
        CROSS JOIN LATERAL (
            VALUES
                ('Payroll - Main Job',       1600.00, 'income',  NULL::TEXT,     NULL::TEXT,      NULL::TEXT,                 NULL::INT),
                ('Payroll - Secondary Job',  2000.00, 'income',  NULL::TEXT,     NULL::TEXT,      NULL::TEXT,                 NULL::INT),
                ('Monthly Saving',            200.00, 'saving',  NULL::TEXT,     NULL::TEXT,      NULL::TEXT,                 NULL::INT),
                ('Rent / Mortgage',           450.00, 'expense', 'monthly',      'Basic Expenses', 'Demo - Current Account',   NULL::INT),
                ('Utilities',                 140.00, 'expense', 'monthly',      'Basic Expenses', 'Demo - Current Account',   NULL::INT),
                ('Groceries',                 330.00, 'expense', 'monthly',      'Food',           'Demo - Shared Card',       NULL::INT),
                ('Transport',                  95.00, 'expense', 'monthly',      'Transport',      'Demo - Main Card',         NULL::INT),
                ('Gym',                        40.00, 'expense', 'monthly',      'Sports',         'Demo - Main Card',         NULL::INT),
                ('Streaming subscriptions',    22.00, 'expense', 'monthly',      'Subscriptions',  'Demo - Shared Card',       NULL::INT),
                ('Leisure activities',        120.00, 'expense', 'monthly',      'Leisure',        'Demo - Main Card',         NULL::INT),
                ('Laptop installment',        180.00, 'expense', 'monthly',      'Home',           'Demo - Main Card',         3)
        ) AS v(concept, base_amount, type, source, category_name, payment_method_name, deferred_total)
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
        WHERE TO_DATE(
            CASE
                WHEN d.type = 'expense' AND COALESCE(d.deferred_total, 1) > 1
                    THEN TO_CHAR((TO_DATE(d.date || '-01', 'YYYY-MM-DD') + ((inst.idx - 1) || ' month')::interval), 'YYYY-MM')
                ELSE d.date
            END || '-01',
            'YYYY-MM-DD'
        ) <= MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::int + 2, 12, 1)
    ),
    inserted AS (
        INSERT INTO records (
            concept, amount, date, type, source, comment, category_id, payment_method_id,
            deferred_index, deferred_total, created_by, created_at, updated_at, updated_by
        )
        SELECT
            concept, amount, date, type, source, comment, category_id, payment_method_id,
            deferred_index, deferred_total, created_by, created_at, updated_at, updated_by
        FROM demo_rows_expanded
        RETURNING 1
    ),
    inserted_loan_payments AS (
        INSERT INTO records (
            concept, amount, date, type, source, comment, category_id, payment_method_id,
            deferred_index, deferred_total, loan_id, is_loan_payment, created_by, created_at, updated_at, updated_by
        )
        SELECT
            lpp.loan_name || ' loan payment',
            lpp.amount,
            lpp.date,
            'expense',
            'monthly',
            demo_tag,
            c.id,
            pm.id,
            NULL,
            NULL,
            lpp.loan_id,
            TRUE,
            actor_username,
            NOW(),
            NOW(),
            actor_username
        FROM loan_payment_plan lpp
        LEFT JOIN categories c ON c.name = 'Basic Expenses'
        LEFT JOIN payment_methods pm ON pm.name = lpp.payment_method_name
        RETURNING 1
    ),
    inserted_loan_usages AS (
        INSERT INTO loan_usages (
            loan_id, concept, amount, date, category_id, comment,
            created_by, created_at, updated_at, updated_by
        )
        SELECT
            lup.loan_id,
            lup.concept,
            lup.amount,
            lup.date,
            c.id,
            demo_tag || ' ' || lup.comment,
            actor_username,
            NOW(),
            NOW(),
            actor_username
        FROM loan_usage_plan lup
        LEFT JOIN categories c ON c.name = lup.category_name
        RETURNING 1
    )
    SELECT
        (SELECT COUNT(*) FROM inserted)
        + (SELECT COUNT(*) FROM inserted_loan_payments)
        + (SELECT COUNT(*) FROM inserted_loan_usages)
    INTO inserted_count;

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
    DELETE FROM loans WHERE description LIKE '[DEMO_SEED_MANAGEMENT]%';
    DELETE FROM settings WHERE key = 'initial_saving';
    DELETE FROM payment_methods pm
    WHERE pm.name IN ('Demo - Main Card', 'Demo - Shared Card', 'Demo - Current Account')
      AND NOT EXISTS (SELECT 1 FROM records r WHERE r.payment_method_id = pm.id);
    DELETE FROM banks b
    WHERE b.name IN ('ING', 'Santander', 'CaixaBank', 'BBVA')
      AND NOT EXISTS (SELECT 1 FROM payment_methods pm WHERE pm.bank_id = b.id)
      AND NOT EXISTS (SELECT 1 FROM loans l WHERE l.bank_id = b.id);
    RETURN deleted_count;
END;
$$;
