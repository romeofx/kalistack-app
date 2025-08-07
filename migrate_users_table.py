import sqlite3

# Connect to the existing database
conn = sqlite3.connect('kalistack.db')
c = conn.cursor()

# Add new columns if they don't exist
try:
    c.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'Free Tier'")
except sqlite3.OperationalError:
    print("Column 'plan' already exists.")

try:
    c.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
except sqlite3.OperationalError:
    print("Column 'last_login' already exists.")

try:
    c.execute("ALTER TABLE users ADD COLUMN tools_used INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    print("Column 'tools_used' already exists.")

# Commit and close
conn.commit()
conn.close()

print("✅ Migration complete: new columns added to 'users' table.")
