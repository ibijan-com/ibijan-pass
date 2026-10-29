import os
import json
import hashlib
from .config import CRYPTO_SERVICES_FILE
from .crypto import get_fernet
from .storage import safe_write_file

class CryptoDataManager:
    def __init__(self):
        self._cache = None
        self._cache_dirty = False

    def get_services(self) -> dict:
        if self._cache is None or self._cache_dirty:
            self._cache = self._load_all()
            self._cache_dirty = False
        return self._cache

    def invalidate_cache(self):
        self._cache_dirty = True

    def _load_all(self) -> dict:
        if os.path.exists(CRYPTO_SERVICES_FILE):
            try:
                with open(CRYPTO_SERVICES_FILE, "rb") as f:
                    encrypted = f.read()
                decrypted = get_fernet().decrypt(encrypted)
                return json.loads(decrypted.decode())
            except Exception as e:
                # DO NOT rename the file. Just report the error.
                raise ValueError(f"Could not load crypto services. File may be corrupted or key is wrong. Details: {e}")
        return {}

crypto_data_manager = CryptoDataManager()

def _get_key(service_name: str, account: str) -> str:
    """Create a unique, collision-free identifier using SHA-256."""
    data = f"{service_name.strip().lower()}|{account.strip().lower()}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def save_crypto_service(service_name: str, account: str, algorithm_version: str, password_revision: int, 
                        length: int, use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool, salt_b64: str) -> tuple[bool, str]:
    
    key = _get_key(service_name, account)
    services = crypto_data_manager.get_services()
    
    # Allow updating an existing service (e.g., changing length)
    new_services = services.copy()
    new_services[key] = {
        "service_name": service_name.strip(),
        "account": account.strip(),
        "algorithm_version": algorithm_version,
        "password_revision": password_revision,
        "length": length,
        "use_upper": use_upper,
        "use_lower": use_lower,
        "use_digits": use_digits,
        "use_symbols": use_symbols,
        "salt": salt_b64
    }

    try:
        encrypted = get_fernet().encrypt(json.dumps(new_services).encode())
        safe_write_file(CRYPTO_SERVICES_FILE, encrypted)
        crypto_data_manager.invalidate_cache()
        return True, "Service settings saved successfully."
    except Exception as e:
        return False, f"Failed to save service: {e}"

def delete_crypto_service(key: str) -> bool:
    services = crypto_data_manager.get_services()
    if key in services:
        new_services = services.copy()
        del new_services[key]
        try:
            encrypted = get_fernet().encrypt(json.dumps(new_services).encode())
            safe_write_file(CRYPTO_SERVICES_FILE, encrypted)
            crypto_data_manager.invalidate_cache()
            return True
        except Exception as e:
            print(f"Error deleting service: {e}")
    return False

def load_crypto_service(key: str) -> dict | None:
    services = crypto_data_manager.get_services()
    return services.get(key)