from cryptography.fernet import Fernet
from utils.secret import SECRET
import base64
import hashlib

# Derive a Fernet key from the SECRET (must be 32 url-safe base64-encoded bytes)
def get_fernet():
    # If SECRET is not 32 bytes, hash or pad it
    key = hashlib.sha256(SECRET.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)
