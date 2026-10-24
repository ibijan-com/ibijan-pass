"""
Storage layer for SPG.

Handles all disk I/O for profiles and the password vault.
Returns (success: bool, message: str) tuples to keep UI logic separate.
"""

import os
import json
from .config import PROFILES_FILE, VAULT_FILE
from .crypto import fernet


class DataManager:
    """Caches profiles in memory to avoid disk reads on every keystroke."""
    def __init__(self):
        self._profiles_cache = None
        self._cache_dirty = False

    def get_profiles(self) -> dict:
        if self._profiles_cache is None or self._cache_dirty:
            self._profiles_cache = self._load_all_profiles()
            self._cache_dirty = False
        return self._profiles_cache

    def invalidate_cache(self):
        self._cache_dirty = True

    def _load_all_profiles(self) -> dict:
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, "rb") as f:
                    encrypted = f.read()
                decrypted = fernet.decrypt(encrypted)
                return json.loads(decrypted.decode())
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {}
        return {}


# Singleton instance
data_manager = DataManager()


# ============================================================
# Profile CRUD
# ============================================================
def save_profile(profile_name, prefix, base_number, special_chars,
                 capitalize_letter="", quotation_style="single",
                 password_pattern="PREFIX + MIDDLE + SPECIAL + END_NUMBER",
                 require_master=False) -> tuple[bool, str]:
    
    profiles = data_manager.get_profiles()
    
    if profile_name in profiles:
        return False, "Profile name already exists!"

    profiles[profile_name] = {
        "prefix": prefix,
        "base_number": base_number,
        "special_chars": special_chars,
        "capitalize_letter": capitalize_letter,
        "quotation_style": quotation_style,
        "password_pattern": password_pattern,
        "require_master": require_master
    }

    try:
        encrypted = fernet.encrypt(json.dumps(profiles).encode())
        with open(PROFILES_FILE, "wb") as f:
            f.write(encrypted)
        data_manager.invalidate_cache()
        return True, f"Profile '{profile_name}' saved successfully!"
    except Exception as e:
        return False, f"Failed to save profile: {e}"


def delete_profile(profile_name: str) -> bool:
    profiles = data_manager.get_profiles()
    if profile_name in profiles:
        del profiles[profile_name]
        try:
            encrypted = fernet.encrypt(json.dumps(profiles).encode())
            with open(PROFILES_FILE, "wb") as f:
                f.write(encrypted)
            data_manager.invalidate_cache()
            return True
        except Exception as e:
            print(f"Error deleting profile: {e}")
    return False


def load_profile(profile_name: str) -> dict | None:
    profiles = data_manager.get_profiles()
    return profiles.get(profile_name)


# ============================================================
# Vault CRUD
# ============================================================
def save_to_vault(service: str, password: str) -> tuple[bool, str]:
    data = []
    
    # Read existing vault
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "rb") as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted).decode()
            lines = decrypted.strip().split("\n")
            for line in lines[1:]:
                if "," in line:
                    svc, pw = line.split(",", 1)
                    data.append((svc, pw))
        except Exception as e:
            return False, f"Could not read vault: {e}"

    # Add new entry and save
    data.append((service, password))
    csv_content = "service,password\n" + "\n".join([f"{s},{p}" for s, p in data])
    
    try:
        encrypted = fernet.encrypt(csv_content.encode())
        with open(VAULT_FILE, "wb") as f:
            f.write(encrypted)
        return True, f"Password for '{service}' saved securely."
    except Exception as e:
        return False, f"Failed to save to vault: {e}"


def get_vault_data() -> str | None:
    """Returns the raw decrypted vault string, or None if empty/error."""
    if not os.path.exists(VAULT_FILE):
        return None
    try:
        with open(VAULT_FILE, "rb") as f:
            encrypted = f.read()
        return fernet.decrypt(encrypted).decode()
    except Exception as e:
        print(f"Vault decryption error: {e}")
        return None


def clear_vault() -> tuple[bool, str]:
    if not os.path.exists(VAULT_FILE):
        return False, "No saved passwords to delete."
    try:
        os.remove(VAULT_FILE)
        return True, "All saved passwords have been permanently deleted."
    except Exception as e:
        return False, f"Could not delete vault: {e}"
