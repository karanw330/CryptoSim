from app.db_init import get_db_connection

conn = get_db_connection()
c = conn.cursor()

c.execute("BEGIN;")

# Add 'side' column to orders table
# SQLite doesn't support ADD COLUMN if NOT EXISTS easily without checking table info, 
# but for a migration we can assume it's needed.
try:
    c.execute("ALTER TABLE orders ADD COLUMN side TEXT;")
    print("Column 'side' added to 'orders' table.")
except Exception as e:
    print(f"Note: {e}")

c.execute("COMMIT;")
conn.close()
print("Migration 0003 completed.")
