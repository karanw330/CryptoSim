from app.db_init import get_db_connection

conn = get_db_connection()
c = conn.cursor()

c.execute("BEGIN;")

# Add 'side' column to orders table
# SQLite doesn't support ADD COLUMN if NOT EXISTS easily without checking table info,
# but for a migration we can assume it's needed.
try:
    c.execute("DELETE FROM trades;")
    c.execute("DELETE FROM orders;")
    c.execute("DELETE FROM portfolio;")
    c.execute("DELETE FROM refresh_tokens;")
    c.execute("DELETE FROM users;")
    c.execute("DELETE FROM sqlite_sequence;")
    c.execute("ALTER TABLE orders ADD COLUMN entry REAL;")
    print("migration 0005: Cleared data and added 'entry' column to 'orders' table.")
except Exception as e:
    print(f"Note: {e}")

c.execute("COMMIT;")
conn.close()
print("Migration 0005 completed.")