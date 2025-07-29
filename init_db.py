import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect('kalistack.db')
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

# Commit and close
conn.commit()
conn.close()

print("✅ Database 'kalistack.db' initialized successfully with 'users' table.")
