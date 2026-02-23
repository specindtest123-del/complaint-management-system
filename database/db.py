import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            sentiment TEXT,
            sentiment_score REAL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@system.com', 'admin123', 1))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('complaints.db')
    conn.row_factory = sqlite3.Row
    return conn