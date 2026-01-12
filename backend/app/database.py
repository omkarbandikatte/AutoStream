import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List

DATABASE_PATH = "app/users.db"

def init_database():
    """Initialize the database with users table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        platform TEXT NOT NULL,
        plan TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new_lead'
    )
    """)
    
    conn.commit()
    conn.close()

def save_user(name: str, email: str, platform: str, plan: str = None) -> bool:
    """Save user details to database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO users (name, email, platform, plan, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (name, email, platform, plan, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Email already exists
        return False
    except Exception as e:
        print(f"Error saving user: {e}")
        return False

def get_user(email: str) -> Optional[Dict]:
    """Get user details by email"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, email, platform, plan, created_at, status
        FROM users WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "platform": row[3],
                "plan": row[4],
                "created_at": row[5],
                "status": row[6]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_all_users() -> List[Dict]:
    """Get all users from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, email, platform, plan, created_at, status
        FROM users ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "platform": row[3],
                "plan": row[4],
                "created_at": row[5],
                "status": row[6]
            })
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def update_user_status(email: str, status: str) -> bool:
    """Update user status"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE users SET status = ? WHERE email = ?
        """, (status, email))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user status: {e}")
        return False

init_database()
