import os
import logging

logger = logging.getLogger("finance.migrations")


def apply_migrations(conn):
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    os.makedirs(migrations_dir, exist_ok=True)

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT NOW()
            )
            """
        )
        conn.commit()

        cur.execute("SELECT id FROM migrations")
        applied = {row[0] for row in cur.fetchall()}
        applied_count = 0

        for filename in sorted(f for f in os.listdir(migrations_dir) if f.endswith(".sql")):
            if filename in applied:
                continue
            path = os.path.join(migrations_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read().strip()
            if not sql:
                continue
            logger.info("migration_apply_start id=%s", filename)
            cur.execute(sql)
            cur.execute("INSERT INTO migrations (id) VALUES (%s)", (filename,))
            conn.commit()
            applied_count += 1
            logger.info("migration_apply_done id=%s", filename)
        logger.info("migration_summary applied=%s skipped=%s", applied_count, len(applied))
