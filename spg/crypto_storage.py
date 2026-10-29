"""
Storage layer for Cryptographic Mode.
Handles saving and loading of service metadata (NOT the generated passwords).
"""

import os
import json
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
                raise ValueError(f"Error reading crypto services: {str(e)}")
        return {}

crypto_data_manager = CryptoDataManager()

def save_crypto_service(service_name: str, account: str, version: int, length: int, 
                        use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool, salt_b64: str) -> tuple[bool, str]:
    services = crypto_data_manager.get_services()
    
    if service_name in services:
        return False, "A service with this name already exists in Cryptographic Mode."

    new_services = services.copy()
    new_services[service_name] = {
        "account": account,
        "version": version,
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
        return True, f"Service '{service_name}' saved successfully."
    except Exception as e:
        return False, f"Failed to save service: {e}"

def delete_crypto_service(service_name: str) -> bool:
    services = crypto_data_manager.get_services()
    if service_name in services:
        new_services = services.copy()
        del new_services[service_name]
        try:
            encrypted = get_fernet().encrypt(json.dumps(new_services).encode())
            safe_write_file(CRYPTO_SERVICES_FILE, encrypted)
            crypto_data_manager.invalidate_cache()
            return True
        except Exception as e:
            print(f"Error deleting service: {e}")
    return False

def load_crypto_service(service_name: str) -> dict | None:
    services = crypto_data_manager.get_services()
    return services.get(service_name)
