from app.db_init import get_db_connection

conn = get_db_connection()
c = conn.cursor()

c.execute("BEGIN;")

# Add 'side' column to orders table
# SQLite doesn't support ADD COLUMN if NOT EXISTS easily without checking table info,
# but for a migration we can assume it's needed.
try:
    c.execute("ALTER TABLE trades ADD COLUMN entry REAL;")
    print("Column 'entry' added to 'trades' table.")
except Exception as e:
    print(f"Note: {e}")

c.execute("COMMIT;")
conn.close()
print("Migration 0004 completed.")