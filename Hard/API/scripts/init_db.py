import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('./db/user_data.db')
cursor = conn.cursor()

# Create a table to hold user credentials
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        note TEXT
    )
''')

# Insert sample data into the table
cursor.execute("INSERT INTO users (username, password, note) VALUES ('admin', 'adminpass', 'Administrator account')")
cursor.execute("INSERT INTO users (username, password, note) VALUES ('user1', 'user1pass', 'First user account')")
cursor.execute("INSERT INTO users (username, password, note) VALUES ('user2', 'user2pass', 'ACVCTF{1518e1b96b7c973022408261c1a53a54}')")

# Save the changes and close the connection
conn.commit()
conn.close()