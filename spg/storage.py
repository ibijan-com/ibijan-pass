import os
import json
import csv
import io
from cryptography.fernet import InvalidToken
from .config import PROFILES_FILE, VAULT_FILE
from .crypto import get_fernet

class DataManager:
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
                decrypted = get_fernet().decrypt(encrypted)
                return json.loads(decrypted.decode())
            except InvalidToken:
                raise ValueError("Could not decrypt profiles. The file is corrupted.")
            except Exception as e:
                raise ValueError(f"Error reading profiles file: {str(e)}")
        return {}

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
        encrypted = get_fernet().encrypt(json.dumps(profiles).encode())
        with open(PROFILES_FILE, "wb") as f:
            f.write(encrypted)
        if os.name == 'posix':
            os.chmod(PROFILES_FILE, 0o600)
        data_manager.invalidate_cache()
        return True, f"Profile '{profile_name}' saved successfully!"
    except Exception as e:
        return False, f"Failed to save profile: {e}"


def delete_profile(profile_name: str) -> bool:
    profiles = data_manager.get_profiles()
    if profile_name in profiles:
        del profiles[profile_name]
        try:
            encrypted = get_fernet().encrypt(json.dumps(profiles).encode())
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
def save_to_vault(service: str, password: str, note: str = "") -> tuple[bool, str]:
    data = []
    
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "rb") as f:
                encrypted = f.read()
            decrypted = get_fernet().decrypt(encrypted).decode()
            reader = csv.reader(io.StringIO(decrypted.strip()))
            next(reader, None) 
            for row in reader:
                if len(row) >= 2:
                    svc = row[0]
                    pw = row[1]
                    nt = row[2] if len(row) > 2 else ""
                    data.append((svc, pw, nt))
        except InvalidToken:
            return False, "Vault encryption key mismatch. The Vault file is corrupted."
        except Exception as e:
            return False, f"Could not read vault: {str(e) or type(e).__name__}"

    if any(item[0] == service and item[1] == password for item in data):
        return False, "This exact password is already saved for this service!"

    data.append((service, password, note))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["service", "password", "note"])
    writer.writerows(data)
    csv_content = output.getvalue()
    
    try:
        encrypted = get_fernet().encrypt(csv_content.encode())
        with open(VAULT_FILE, "wb") as f:
            f.write(encrypted)
        if os.name == 'posix':
            os.chmod(VAULT_FILE, 0o600)
        return True, f"Password for '{service}' saved securely."
    except Exception as e:
        return False, f"Failed to save to vault: {e}"


def get_vault_data() -> list[tuple[str, str, str]] | None:
    if not os.path.exists(VAULT_FILE):
        return None
    try:
        with open(VAULT_FILE, "rb") as f:
            encrypted = f.read()
        decrypted = get_fernet().decrypt(encrypted).decode()
        
        reader = csv.reader(io.StringIO(decrypted.strip()))
        next(reader, None) 
        data = []
        for row in reader:
            if len(row) >= 2:
                data.append((row[0], row[1], row[2] if len(row) > 2 else ""))
        return data
    except Exception as e:
        raise ValueError(f"Vault decryption error: {e}")


def clear_vault() -> tuple[bool, str]:
    if not os.path.exists(VAULT_FILE):
        return False, "No saved passwords to delete."
    try:
        os.remove(VAULT_FILE)
        return True, "All saved passwords have been permanently deleted."
    except Exception as e:
        return False, f"Could not delete vault: {e}"