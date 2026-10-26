"""
Backup (Export/Import) logic for SPG.

Encrypts backups using a password-derived key so they can be
restored on ANY machine, even after a Factory Reset.
"""

import os
import json
import base64
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet, InvalidToken

from .config import VAULT_FILE, PROFILES_FILE
from .storage import data_manager
from .dialogs import show_custom_error
from .crypto import fernet as local_fernet

def _derive_key(password: str) -> bytes:
    """Derive a valid Fernet key from a simple text password."""
    if not password:
        # Default fallback key for passwordless backups (portable and simple)
        password = "ibijan-pass-portable-backup-key"
    # Hash the password with SHA-256 to get a 32-byte key, then base64 encode it for Fernet
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def _export_data(export_type, file_path, password=None) -> tuple[bool, str]:
    try:
        export_payload = {
            "version": "0.9.2",
            "export_date": datetime.now().isoformat(),
            "type": export_type,
            "data": {}
        }
        
        if export_type in ['profiles', 'all']:
            export_payload["data"]["profiles"] = data_manager.get_profiles()
        
        if export_type in ['vault', 'all'] and os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, "rb") as f:
                vault_encrypted = f.read()
            try:
                # Decrypt vault using the local machine's key and store raw text in the backup
                vault_decrypted = local_fernet.decrypt(vault_encrypted).decode()
                export_payload["data"]["vault_text"] = vault_decrypted
            except Exception:
                pass # Skip if vault is empty or corrupted
        
        # Encrypt using the password-derived key
        key = _derive_key(password)
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(export_payload).encode())
        
        with open(file_path, "wb") as out_f:
            out_f.write(encrypted_data)
        return True, "Export completed successfully!"
    except Exception as e:
        return False, f"Export failed: {e}"

def _import_data(file_path, password=None) -> tuple[bool, str]:
    try:
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        
        # Decrypt using the password-derived key
        key = _derive_key(password)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        import_payload = json.loads(decrypted_data.decode())
        
        if "version" not in import_payload or "data" not in import_payload:
            return False, "Invalid import file format."
        
        imported_profiles = 0
        imported_vault = 0
        
        if "profiles" in import_payload["data"]:
            current_profiles = data_manager.get_profiles()
            for name, data in import_payload["data"]["profiles"].items():
                if name not in current_profiles:
                    current_profiles[name] = data
                    imported_profiles += 1
            
            # Save back using the local system's secure key
            encrypted_profiles = local_fernet.encrypt(json.dumps(current_profiles).encode())
            with open(PROFILES_FILE, "wb") as out_f:
                out_f.write(encrypted_profiles)
            data_manager.invalidate_cache()
        
        # If backup contains raw vault text, encrypt it with the current local key
        if "vault_text" in import_payload["data"]:
            vault_text = import_payload["data"]["vault_text"]
            vault_encrypted = local_fernet.encrypt(vault_text.encode())
            with open(VAULT_FILE, "wb") as out_f:
                out_f.write(vault_encrypted)
            imported_vault += 1
        elif "vault" in import_payload["data"]:
            return False, "This backup file is from an older version and cannot be restored after a factory reset. Please create a new backup from the original system."
        
        return True, f"Import completed!\nProfiles restored: {imported_profiles}\nVault items restored: {imported_vault}"
    
    except InvalidToken:
        return False, "Incorrect Password!\n\nThe password you entered does not match this backup file. Please try again."
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
    
    # Simple Password Field instead of complex keys
    tk.Label(export_window, text="Backup Password (Optional but recommended):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    pw_entry = tk.Entry(export_window, width=40, show="*")
    pw_entry.pack(pady=2)
    
    warning_lbl = tk.Label(export_window, text="If you set a password, you MUST remember it to import this file later.", font=("Helvetica", 8), fg="#CC3333")
    warning_lbl.pack(pady=5)
    
    def perform_export():
        password = pw_entry.get().strip()
        file_path = filedialog.asksaveasfilename(defaultextension=".spg", filetypes=[("SPG Backup", "*.spg")], parent=export_window)
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
    
    tk.Label(import_window, text="Backup Password (leave blank if you didn't set one):", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=(10, 5))
    pw_entry = tk.Entry(import_window, width=40, show="*")
    pw_entry.pack(pady=5)
    
    def perform_import():
        password = pw_entry.get().strip()
        file_path = filedialog.askopenfilename(filetypes=[("SPG Backup", "*.spg")], parent=import_window)
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