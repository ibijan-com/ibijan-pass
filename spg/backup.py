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
            "version": "0.9.1",
            "export_date": datetime.now().isoformat(),
            "type": export_type,
            "data": {}
        }
        
        if export_type in ['profiles', 'all']:
            export_payload["data"]["profiles"] = data_manager.get_profiles()
        
        if export_type in ['vault', 'all'] and os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, "rb") as f:
                vault_encrypted = f.read()
            export_payload["data"]["vault"] = base64.b64encode(vault_encrypted).decode()
        
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
        
        imported_count = 0
        
        if "profiles" in import_payload["data"]:
            current_profiles = data_manager.get_profiles()
            for name, data in import_payload["data"]["profiles"].items():
                if name not in current_profiles:
                    current_profiles[name] = data
                    imported_count += 1
            
            # Save back using the local system's secure key (from crypto.py)
            from .crypto import fernet as local_fernet
            encrypted_profiles = local_fernet.encrypt(json.dumps(current_profiles).encode())
            with open(PROFILES_FILE, "wb") as out_f:
                out_f.write(encrypted_profiles)
            data_manager.invalidate_cache()
        
        if "vault" in import_payload["data"]:
            vault_data = base64.b64decode(import_payload["data"]["vault"])
            with open(VAULT_FILE, "wb") as out_f:
                out_f.write(vault_data)
            imported_count += 1
        
        return True, f"Import completed! {imported_count} items restored."
    
    except InvalidToken:
        return False, "Incorrect Password!\n\nThe password you entered does not match this backup file. Please try again."
    except Exception as e:
        return False, f"Import failed: {str(e)}"


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