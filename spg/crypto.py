import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from .config import CONFIG_DIR, KEY_FILE, PROFILES_FILE, VAULT_FILE

class KeyIntegrityError(Exception):
    pass

class DataMissingError(Exception):
    pass

_fernet_instance = None

def set_fernet(instance: Fernet):
    global _fernet_instance
    _fernet_instance = instance

def get_fernet() -> Fernet:
    if _fernet_instance is None:
        raise KeyIntegrityError("Data key not loaded. Please authenticate first.")
    return _fernet_instance

def lock_fernet():
    """Removes the active data key from memory."""
    global _fernet_instance
    _fernet_instance = None

def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key using scrypt."""
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def is_master_set() -> bool:
    """Check if the Master Password is set, preventing the 'New Install' trap."""
    key_exists = os.path.exists(KEY_FILE)
    data_exists = os.path.exists(PROFILES_FILE) or os.path.exists(VAULT_FILE)

    if not key_exists and data_exists:
        raise KeyIntegrityError(
            "CRITICAL SECURITY ERROR:\n\n"
            "The encryption key (key.key) is missing, but encrypted data exists.\n"
            "The application cannot access your data without the key.\n\n"
            "If you have a .ibpass backup file, please use Factory Reset, then Import your backup."
        )
    
    return key_exists

def setup_master_password(password: str):
    """Creates the master key file, generating a random data key and encrypting it."""
    if not password:
        raise ValueError("Password cannot be empty.")

    if os.path.exists(KEY_FILE):
        raise ValueError("Master password is already set.")

    if os.path.exists(PROFILES_FILE) or os.path.exists(VAULT_FILE):
        raise ValueError("Data files exist but key is missing. Factory Reset is required.")

    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.name == 'posix':
        os.chmod(CONFIG_DIR, 0o700)

    salt = os.urandom(16)
    master_key = _derive_key(password, salt)
    
    data_key = Fernet.generate_key()
    f_master = Fernet(master_key)
    encrypted_data_key = f_master.encrypt(data_key)

    key_payload = {
        "version": "1.0",
        "salt": base64.b64encode(salt).decode('utf-8'),
        "encrypted_data_key": encrypted_data_key.decode('utf-8')
    }

    with open(KEY_FILE, "w") as f:
        json.dump(key_payload, f)
    
    if os.name == 'posix':
        os.chmod(KEY_FILE, 0o600)

    set_fernet(Fernet(data_key))

def verify_master_password(password: str) -> bool:
    """Verifies the master password and loads the data key into memory."""
    if not os.path.exists(KEY_FILE):
        return False

    try:
        with open(KEY_FILE, "r") as f:
            key_payload = json.load(f)
        
        if "encrypted_data_key" not in key_payload:
            raise KeyIntegrityError("Incompatible key format. Factory Reset required.")

        salt = base64.b64decode(key_payload["salt"])
        encrypted_data_key = key_payload["encrypted_data_key"].encode('utf-8')

        master_key = _derive_key(password, salt)
        f_master = Fernet(master_key)
        
        data_key = f_master.decrypt(encrypted_data_key)
        set_fernet(Fernet(data_key))
        return True

    except Exception:
        return False