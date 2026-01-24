from typing import Dict, Any, Optional
from .connection import get_connection

def get_password_by_key(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve a password entry by key."""
    with get_connection() as conn:
        cur = conn.execute('SELECT id, key, password FROM passwords WHERE key = ?', (key,))
        row = cur.fetchone()
        if row:
            return {'id': row[0], 'key': row[1], 'password': row[2]}
        return None

def store_password(key: str, password: str) -> Dict[str, Any]:
    """Encrypt and store a password with a key. Overwrites if key exists."""
    from utils.crypto import get_fernet
    f = get_fernet()
    encrypted = f.encrypt(password.encode()).decode()
    
    with get_connection() as conn:
        # Check if exists
        cur = conn.execute('SELECT id FROM passwords WHERE key = ?', (key,))
        existing = cur.fetchone()
        
        if existing:
            conn.execute('UPDATE passwords SET password = ? WHERE key = ?', (encrypted, key))
            pw_id = existing[0]
        else:
            cur = conn.execute('INSERT INTO passwords (key, password) VALUES (?, ?)', (key, encrypted))
            pw_id = cur.lastrowid
            
        conn.commit()
        return {'id': pw_id, 'key': key, 'password': encrypted}

def get_decrypted_password(key: str) -> Optional[str]:
    """Retrieve and decrypt the password for a given key."""
    pw = get_password_by_key(key)
    if not pw:
        return None
        
    from utils.crypto import get_fernet
    try:
        f = get_fernet()
        return f.decrypt(pw['password'].encode()).decode()
    except Exception as e:
        print(f"Error decrypting password for key {key}: {e}")
        return None
