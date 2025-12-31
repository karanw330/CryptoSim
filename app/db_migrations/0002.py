from app.db_init import get_db_connection

conn = get_db_connection()
c = conn.cursor()

c.execute("BEGIN;")

# Create Refresh Tokens Table
c.execute('''
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        token TEXT UNIQUE,
        expires_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(username)
    )
''')

c.execute("COMMIT;")
conn.close()
print("Migration 0002 completed: refresh_tokens table created.")
