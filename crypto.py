"""
Cryptographic primitives for SPG.

Handles:
- Fernet key generation and loading
- Master password hashing (SHA-256)
- Master password verification

Depends on: config.py only.
"""

import os
import hashlib
from cryptography.fernet import Fernet

from .config import CONFIG_DIR, KEY_FILE, MASTER_HASH_FILE


# ============================================================
# Fernet key management
# ============================================================
def load_or_create_key() -> Fernet:
    """
    Load the Fernet encryption key from disk, or create it if it
    doesn't exist.

    The key file is stored at ~/.spg/key.key.

    Returns:
        Fernet: An initialized Fernet instance ready for encrypt/decrypt.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()

    return Fernet(key)


# Singleton Fernet instance — imported by storage.py, backup.py, etc.
fernet = load_or_create_key()


# ============================================================
# Master password hashing
# ============================================================
def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()


def is_master_set() -> bool:
    """Return True if a master password has already been configured."""
    return os.path.exists(MASTER_HASH_FILE)


def save_master_hash(hashed_pw: str) -> None:
    """Persist the (already-hashed) master password to disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(MASTER_HASH_FILE, "w") as f:
        f.write(hashed_pw)


def verify_master(password: str) -> bool:
    """
    Check if the given plaintext password matches the stored hash.

    Returns:
        bool: True if match, False otherwise (or if no master is set).
    """
    if not is_master_set():
        return False
    with open(MASTER_HASH_FILE, "r") as f:
        stored_hash = f.read().strip()
    return hash_password(password) == stored_hash
