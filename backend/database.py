import sqlite3
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from contextlib import contextmanager

DB_FILE = "users.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize the SQLite database with users, sessions, evaluations, and comparisons tables"""
    with get_db_connection() as conn:
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
        
        # Create evaluations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                content TEXT,
                result TEXT NOT NULL,
                total_score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create comparisons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_statement TEXT NOT NULL,
                solution1_type TEXT NOT NULL,
                solution1_content TEXT NOT NULL,
                solution2_type TEXT NOT NULL,
                solution2_content TEXT NOT NULL,
                cfg1_json TEXT NOT NULL,
                cfg2_json TEXT NOT NULL,
                comparison_result TEXT NOT NULL,
                winner TEXT NOT NULL,
                overall_scores TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(email: str, password: str) -> Tuple[bool, str]:
    """Create a new user. Returns (success, message)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash)
            )
            conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "User already exists"
    except Exception as e:
        return False, str(e)

def verify_user(email: str, password: str) -> Optional[int]:
    """Verify user credentials. Returns user_id if valid, None otherwise"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE email = ?",
                (email,)
            )
            result = cursor.fetchone()
            
            if result and verify_password(password, result[1]):
                return result[0]
            return None
    except Exception:
        return None

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

def save_evaluation(user_id: int, eval_type: str, content: str, result: dict) -> int:
    """Save an evaluation result. Returns evaluation_id"""
    import json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO evaluations (user_id, type, content, result, total_score) VALUES (?, ?, ?, ?, ?)",
                (user_id, eval_type, content, json.dumps(result), result.get('total_score', 0))
            )
            eval_id = cursor.lastrowid
            conn.commit()
            return eval_id
    except Exception:
        return 0

def get_user_evaluations(user_id: int, limit: int = 10):
    """Get recent evaluations for a user"""
    import json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, type, content, result, total_score, created_at FROM evaluations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
            results = cursor.fetchall()
            
            evaluations = []
            for row in results:
                evaluations.append({
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'result': json.loads(row[3]),
                    'total_score': row[4],
                    'created_at': row[5]
                })
            return evaluations
    except Exception:
        return []

def save_comparison(user_id: int, problem_statement: str, solution1_type: str, solution1_content: str,
                   solution2_type: str, solution2_content: str, cfg1_json: str, cfg2_json: str,
                   comparison_result: dict, winner: str, overall_scores: dict) -> int:
    """Save a solution comparison. Returns comparison_id"""
    import json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO comparisons (user_id, problem_statement, solution1_type, solution1_content,
                   solution2_type, solution2_content, cfg1_json, cfg2_json, comparison_result, winner, overall_scores)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, problem_statement, solution1_type, solution1_content[:1000],
                 solution2_type, solution2_content[:1000], cfg1_json, cfg2_json,
                 json.dumps(comparison_result), winner, json.dumps(overall_scores))
            )
            comp_id = cursor.lastrowid
            conn.commit()
            return comp_id
    except Exception:
        return 0


def get_user_comparisons(user_id: int, limit: int = 20):
    """Get recent comparisons for a user"""
    import json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, problem_statement, solution1_type, solution2_type, winner, 
                   overall_scores, comparison_result, created_at 
                   FROM comparisons WHERE user_id = ? ORDER BY created_at DESC LIMIT ?""",
                (user_id, limit)
            )
            results = cursor.fetchall()
            
            comparisons = []
            for row in results:
                comparisons.append({
                    'id': row[0],
                    'problem_statement': row[1],
                    'solution1_type': row[2],
                    'solution2_type': row[3],
                    'winner': row[4],
                    'overall_scores': json.loads(row[5]),
                    'comparison_result': json.loads(row[6]),
                    'created_at': row[7]
                })
            return comparisons
    except Exception:
        return []


def get_comparison_by_id(comparison_id: int, user_id: int):
    """Get a specific comparison by ID"""
    import json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, problem_statement, solution1_type, solution1_content, solution2_type, 
                   solution2_content, cfg1_json, cfg2_json, comparison_result, winner, overall_scores, created_at
                   FROM comparisons WHERE id = ? AND user_id = ?""",
                (comparison_id, user_id)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'id': row[0],
                'problem_statement': row[1],
                'solution1_type': row[2],
                'solution1_content': row[3],
                'solution2_type': row[4],
                'solution2_content': row[5],
                'cfg1_json': json.loads(row[6]),
                'cfg2_json': json.loads(row[7]),
                'comparison_result': json.loads(row[8]),
                'winner': row[9],
                'overall_scores': json.loads(row[10]),
                'created_at': row[11]
            }
    except Exception:
        return None


# Initialize database on module import
init_database()
