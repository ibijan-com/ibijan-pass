import os
import json
import base64
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .config import VAULT_FILE, PROFILES_FILE
from .storage import data_manager
from .dialogs import show_custom_error
from .crypto import get_fernet

def _derive_backup_key(password: str, salt: bytes) -> bytes:
    """Derive a key for backup encryption using scrypt."""
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def _export_data(export_type, file_path, password=None) -> tuple[bool, str]:
    temp_path = file_path + ".tmp"
    try:
        if not password:
            return False, "Export failed: A backup password is required to secure your data."

        export_payload = {
            "version": "1.0.0",
            "export_date": datetime.now().isoformat(),
            "type": export_type,
            "data": {}
        }
        
        if export_type in ['profiles', 'all']:
            export_payload["data"]["profiles"] = data_manager.get_profiles()
        
        if export_type in ['vault', 'all']:
            if os.path.exists(VAULT_FILE):
                with open(VAULT_FILE, "rb") as f:
                    vault_encrypted = f.read()
                try:
                    vault_decrypted = get_fernet().decrypt(vault_encrypted).decode()
                    export_payload["data"]["vault_text"] = vault_decrypted
                except Exception as e:
                    return False, f"Export failed: The Vault is corrupted.\nDetails: {e}"
            else:
                if export_type == 'vault':
                    return False, "Export failed: No Vault file exists to export."
        
        # Encrypt using the password-derived key
        salt = os.urandom(16)
        key = _derive_backup_key(password, salt)
        f = Fernet(key)
        
        json_bytes = json.dumps(export_payload).encode()
        encrypted_data = f.encrypt(json_bytes)
        
        final_output = {
            "salt": base64.b64encode(salt).decode('utf-8'),
            "payload": encrypted_data.decode('utf-8')
        }
        
        # Atomic write: write to temp file first, then replace
        with open(temp_path, "w") as out_f:
            json.dump(final_output, out_f)
        os.replace(temp_path, file_path)
        
        return True, "Export completed successfully!"
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, f"Export failed: {e}"

def _import_data(file_path, password=None) -> tuple[bool, str]:
    try:
        if not password:
            return False, "Import failed: Password is required."

        with open(file_path, "r") as f:
            file_payload = json.load(f)
            
        if "salt" not in file_payload or "payload" not in file_payload:
            return False, "Invalid or unsupported backup file format."

        salt = base64.b64decode(file_payload["salt"])
        encrypted_data = file_payload["payload"].encode('utf-8')
        
        key = _derive_backup_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        import_payload = json.loads(decrypted_data.decode())
        
        if "data" not in import_payload:
            return False, "Invalid import file format."
        
        imported_profiles = 0
        imported_vault = 0
        
        if "profiles" in import_payload["data"]:
            current_profiles = data_manager.get_profiles()
            for name, data in import_payload["data"]["profiles"].items():
                if name not in current_profiles:
                    current_profiles[name] = data
                    imported_profiles += 1
            
            encrypted_profiles = get_fernet().encrypt(json.dumps(current_profiles).encode())
            with open(PROFILES_FILE, "wb") as out_f:
                out_f.write(encrypted_profiles)
            data_manager.invalidate_cache()
        
        if "vault_text" in import_payload["data"]:
            vault_text = import_payload["data"]["vault_text"]
            vault_encrypted = get_fernet().encrypt(vault_text.encode())
            with open(VAULT_FILE, "wb") as out_f:
                out_f.write(vault_encrypted)
            imported_vault += 1
        
        return True, f"Import completed!\nProfiles restored: {imported_profiles}\nVault items restored: {imported_vault}"
    
    except InvalidToken:
        return False, "Incorrect Password!\n\nThe password you entered does not match this backup file."
    except Exception as e:
        return False, f"Import failed: {str(e)}"


# ==========================================
# UI Dialogs for Backup
# ==========================================
def show_export_dialog(root):
    export_window = tk.Toplevel(root)
    export_window.title("Export Data")
    export_window.geometry("480x380")
    export_window.transient(root)
    export_window.grab_set()
    export_window.resizable(False, False)
    
    tk.Label(export_window, text="📤 Export Backup", font=("Helvetica", 14, "bold"), fg="#1C39BB").pack(pady=10)
    
    tk.Label(export_window, text="Select data to export:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=20, pady=5)
    export_var = tk.StringVar(value="all")
    tk.Radiobutton(export_window, text="Profiles Only (Settings & Patterns)", variable=export_var, value="profiles").pack(anchor="w", padx=20)
    tk.Radiobutton(export_window, text="Vault Only (Saved Passwords)", variable=export_var, value="vault").pack(anchor="w", padx=20)
    tk.Radiobutton(export_window, text="All Data (Profiles + Vault)", variable=export_var, value="all").pack(anchor="w", padx=20)
    
    tk.Label(export_window, text="Backup Password (Required for security):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    pw_entry = tk.Entry(export_window, width=40, show="*")
    pw_entry.pack(pady=2)
    
    warning_lbl = tk.Label(export_window, text="You MUST remember this password to import this file later.", font=("Helvetica", 8, "bold"), fg="#CC3333")
    warning_lbl.pack(pady=5)
    
    def perform_export():
        password = pw_entry.get()
        file_path = filedialog.asksaveasfilename(defaultextension=".ibpass", filetypes=[("iBijan Pass Backup", "*.ibpass")], parent=export_window)
        if not file_path: return
        
        success, msg = _export_data(export_var.get(), file_path, password)
        if success:
            messagebox.showinfo("Success", msg, parent=export_window)
            export_window.destroy()
        else:
            show_custom_error(export_window, "Export Error", msg)
    
    tk.Button(export_window, text="Export to File", command=perform_export, bg="#00A693", fg="white", font=("Helvetica", 10, "bold"), width=18).pack(pady=15)


def show_import_dialog(root, on_import_success=None):
    import_window = tk.Toplevel(root)
    import_window.title("Import Data")
    import_window.geometry("450x280")
    import_window.transient(root)
    import_window.grab_set()
    import_window.resizable(False, False)
    
    tk.Label(import_window, text="📥 Import Backup", font=("Helvetica", 14, "bold"), fg="#1C39BB").pack(pady=10)
    
    tk.Label(import_window, text="Backup Password:", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=(10, 5))
    pw_entry = tk.Entry(import_window, width=40, show="*")
    pw_entry.pack(pady=5)
    
    def perform_import():
        password = pw_entry.get()
        file_path = filedialog.askopenfilename(filetypes=[("iBijan Pass Backup", "*.ibpass")], parent=import_window)
        if not file_path: return
        
        success, msg = _import_data(file_path, password)
        if success:
            messagebox.showinfo("Success", msg, parent=import_window)
            import_window.destroy()
            if on_import_success:
                on_import_success()
        else:
            show_custom_error(import_window, "Import Failed", msg)
    
    tk.Button(import_window, text="Select File & Import", command=perform_import, bg="#1C39BB", fg="white", font=("Helvetica", 10, "bold"), width=18).pack(pady=20)