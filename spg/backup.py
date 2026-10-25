"""
Data backup (Export/Import) logic for SPG.
"""

import os
import json
import base64
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog

from .config import VAULT_FILE, PROFILES_FILE
from .crypto import fernet
from .storage import data_manager

def _generate_export_key():
    return fernet.generate_key()

def _export_data(export_type, file_path, export_key=None) -> tuple[bool, str]:
    try:
        export_payload = {
            "version": "0.9",
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
        
        if export_key:
            export_fernet = fernet.__class__(export_key)
            encrypted_data = export_fernet.encrypt(json.dumps(export_payload).encode())
        else:
            encrypted_data = fernet.encrypt(json.dumps(export_payload).encode())
        
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
        return True, "Export completed successfully!"
    except Exception as e:
        return False, f"Export failed: {e}"

def _import_data(file_path, import_key=None) -> tuple[bool, str]:
    try:
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        
        if import_key:
            import_fernet = fernet.__class__(import_key)
            decrypted_data = import_fernet.decrypt(encrypted_data)
        else:
            decrypted_data = fernet.decrypt(encrypted_data)
        
        import_payload = json.loads(decrypted_data.decode())
        
        if "version" not in import_payload or "data" not in import_payload:
            return False, "Invalid import file format"
        
        imported_count = 0
        
        if "profiles" in import_payload["data"]:
            current_profiles = data_manager.get_profiles()
            for name, data in import_payload["data"]["profiles"].items():
                if name not in current_profiles:
                    current_profiles[name] = data
                    imported_count += 1
            
            encrypted = fernet.encrypt(json.dumps(current_profiles).encode())
            with open(PROFILES_FILE, "wb") as f:
                f.write(encrypted)
            data_manager.invalidate_cache()
        
        if "vault" in import_payload["data"]:
            vault_data = base64.b64decode(import_payload["data"]["vault"])
            with open(VAULT_FILE, "wb") as f:
                f.write(vault_data)
            imported_count += 1
        
        return True, f"Import completed! {imported_count} items imported."
    except Exception as e:
        return False, f"Import failed: {e}"

# ==========================================
# UI Dialogs for Backup
# ==========================================
def show_export_dialog(root):
    export_window = tk.Toplevel(root)
    export_window.title("Export Data")
    export_window.geometry("450x350")
    export_window.transient(root)
    export_window.grab_set()
    export_window.resizable(False, False)

    tk.Label(export_window, text="📤 Export Data", font=("Arial", 14, "bold"), fg="#1C39BB").pack(pady=10)
    
    tk.Label(export_window, text="Select data to export:").pack(anchor="w", padx=20, pady=5)
    export_var = tk.StringVar(value="all")
    tk.Radiobutton(export_window, text="Profiles Only", variable=export_var, value="profiles").pack(anchor="w", padx=20)
    tk.Radiobutton(export_window, text="Vault Only", variable=export_var, value="vault").pack(anchor="w", padx=20)
    tk.Radiobutton(export_window, text="All Data", variable=export_var, value="all").pack(anchor="w", padx=20)
    
    encrypt_var = tk.BooleanVar(value=False)
    tk.Checkbutton(export_window, text="Encrypt with separate key (Extra Secure)", variable=encrypt_var).pack(anchor="w", padx=20, pady=10)
    
    key_label = tk.Label(export_window, text="", font=("Arial", 8), wraplength=400, fg="gray")
    key_label.pack(pady=5)
    
    export_key = None
    def generate_key():
        nonlocal export_key
        export_key = _generate_export_key()
        key_label.config(text=f"Key: {base64.b64encode(export_key).decode()}\n(Save this key, you will need it to import!)")
    
    tk.Button(export_window, text="Generate Key", command=generate_key).pack(pady=5)
    
    def perform_export():
        nonlocal export_key
        file_path = filedialog.asksaveasfilename(defaultextension=".spg", filetypes=[("SPG Backup", "*.spg")])
        if not file_path: return
        
        success, msg = _export_data(export_var.get(), file_path, export_key if encrypt_var.get() else None)
        if success:
            messagebox.showinfo("Success", msg, parent=export_window)
            export_window.destroy()
        else:
            messagebox.showerror("Error", msg, parent=export_window)
    
    tk.Button(export_window, text="Export File", command=perform_export, bg="#00A693", fg="white", font=("Arial", 10, "bold")).pack(pady=15, ipadx=20)

def show_import_dialog(root, on_import_success=None):
    import_window = tk.Toplevel(root)
    import_window.title("Import Data")
    import_window.geometry("450x300")
    import_window.transient(root)
    import_window.grab_set()
    import_window.resizable(False, False)
    tk.Label(import_window, text="📥 Import Data", font=("Arial", 14, "bold"), fg="#1C39BB").pack(pady=10)
    
    tk.Label(import_window, text="Import Key (if encrypted):").pack(anchor="w", padx=20, pady=5)
    key_entry = tk.Entry(import_window, width=50)
    key_entry.pack(pady=5)
    
    def perform_import():
        file_path = filedialog.askopenfilename(filetypes=[("SPG Backup", "*.spg")])
        if not file_path: return
        
        import_key = None
        if key_entry.get().strip():
            try:
                import_key = base64.b64decode(key_entry.get().strip())
            except Exception:
                messagebox.showerror("Error", "Invalid key format!", parent=import_window)
                return
        
        success, msg = _import_data(file_path, import_key)
        if success:
            messagebox.showinfo("Success", msg, parent=import_window)
            import_window.destroy()
            if on_import_success:
                on_import_success()
        else:
            messagebox.showerror("Error", msg, parent=import_window)
    
    tk.Button(import_window, text="Select File & Import", command=perform_import, bg="#1C39BB", fg="white", font=("Arial", 10, "bold")).pack(pady=20, ipadx=20)
