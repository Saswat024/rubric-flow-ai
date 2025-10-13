import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

DB_FILE = "users.db"

def init_database():
    """Initialize the SQLite database with users and sessions tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email: str, password: str) -> Tuple[bool, str]:
    """Create a new user. Returns (success, message)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )
        
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "User already exists"
    except Exception as e:
        return False, str(e)

def verify_user(email: str, password: str) -> Optional[int]:
    """Verify user credentials. Returns user_id if valid, None otherwise"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute(
        "SELECT id FROM users WHERE email = ? AND password_hash = ?",
        (email, password_hash)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def create_session(user_id: int) -> str:
    """Create a new session for a user. Returns session token"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)
    
    cursor.execute(
        "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires_at)
    )
    
    conn.commit()
    conn.close()
    
    return token

def verify_session(token: str) -> Optional[int]:
    """Verify a session token. Returns user_id if valid, None otherwise"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT user_id FROM sessions WHERE token = ? AND expires_at > ?",
        (token, datetime.now())
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def delete_session(token: str) -> bool:
    """Delete a session token. Returns True if successful"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_user_email(user_id: int) -> Optional[str]:
    """Get user email by user_id"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

# Initialize database on module import
init_database()
