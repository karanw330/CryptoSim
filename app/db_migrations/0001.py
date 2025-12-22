from app.db_init import get_db_connection

conn = get_db_connection()
c = conn.cursor()

c.execute("PRAGMA foreign_keys = OFF;")
c.execute("BEGIN;")

# 1. Create new table
c.execute("""
CREATE TABLE users_new (
    username TEXT PRIMARY KEY,
    email TEXT,
    sub TEXT,
    hashed_password TEXT,
    disabled INTEGER DEFAULT 0,
    balance_usd REAL DEFAULT 100000.0
)
""")

# 2. Copy old data (map columns explicitly)
c.execute("""
INSERT INTO users_new (username, email, hashed_password, disabled, balance_usd)
SELECT username, email, hashed_password, disabled, balance_usd
FROM users
""")

# 3. Drop old table
c.execute("DROP TABLE users;")

# 4. Rename
c.execute("ALTER TABLE users_new RENAME TO users;")

c.execute("COMMIT;")
c.execute("PRAGMA foreign_keys = ON;")

conn.close()

