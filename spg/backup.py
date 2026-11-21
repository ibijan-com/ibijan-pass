import os
import json
import base64
import io
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .config import VAULT_FILE, PROFILES_FILE, CRYPTO_SERVICES_FILE
from .storage import data_manager, safe_write_file
from .crypto_storage import crypto_data_manager
from .dialogs import show_custom_error
from .crypto import get_fernet

def _derive_backup_key(password: str, salt: bytes, n: int) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=n, r=8, p=1)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def _export_data(export_type, file_path, password=None) -> tuple[bool, str]:
    try:
        if not password:
            return False, "Export failed: A backup password is required."

        export_payload = {
            "version": "1.1.0",
            "export_date": datetime.now().isoformat(),
            "type": export_type,
            "data": {}
        }
        
        if export_type in ['profiles', 'all']:
            export_payload["data"]["profiles"] = data_manager.get_profiles()
            export_payload["data"]["crypto_services"] = crypto_data_manager.get_services()
        
        if export_type in ['vault', 'all']:
            if os.path.exists(VAULT_FILE):
                with open(VAULT_FILE, "rb") as f:
                    vault_encrypted = f.read()
                try:
                    vault_decrypted = get_fernet().decrypt(vault_encrypted).decode()
                    export_payload["data"]["vault_text"] = vault_decrypted
                except Exception as e:
                    return False, f"Export failed: The Vault is corrupted and cannot be exported.\nDetails: {e}"
            else:
                if export_type == 'vault':
                    return False, "Export failed: No Vault file exists to export."
        
        salt = os.urandom(16)
        current_n = 2**16 # Use strong KDF for new backups
        
        key = _derive_backup_key(password, salt, current_n)
        f = Fernet(key)
        
        json_bytes = json.dumps(export_payload).encode()
        encrypted_data = f.encrypt(json_bytes)
        
        final_output = {
            "kdf_n": current_n, # Store KDF param
            "salt": base64.b64encode(salt).decode('utf-8'),
            "payload": encrypted_data.decode('utf-8')
        }
        
        final_bytes = json.dumps(final_output).encode('utf-8')
        safe_write_file(file_path, final_bytes)
        
        return True, "Export completed successfully!"
        
    except Exception as e:
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
        
        # Validate KDF parameter
        kdf_n = file_payload.get("kdf_n", 2**14)
        if not isinstance(kdf_n, int) or kdf_n < 2**14 or kdf_n > 2**20:
            return False, "Invalid KDF parameter in backup file."
        
        key = _derive_backup_key(password, salt, kdf_n)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        import_payload = json.loads(decrypted_data.decode())
        
        if "data" not in import_payload:
            return False, "Invalid import file format."
        
        imported_profiles = 0
        imported_crypto = 0
        vault_merged_count = 0
        
        profiles_to_write = None
        crypto_to_write = None
        vault_to_write = None

        # 1. Prepare Profiles (Keep Existing if Conflict)
        if "profiles" in import_payload["data"]:
            current_profiles = data_manager.get_profiles()
            merged = current_profiles.copy()
            for name, data in import_payload["data"]["profiles"].items():
                if name not in merged:
                    merged[name] = data
                    imported_profiles += 1
                # Note: If name exists, we currently keep the existing one. 
                # (Conflict resolution UI will be added in Phase 2)
            profiles_to_write = get_fernet().encrypt(json.dumps(merged).encode())

        # 2. Prepare Crypto Services (Keep Existing if Conflict)
        if "crypto_services" in import_payload["data"]:
            current_crypto = crypto_data_manager.get_services()
            merged_crypto = current_crypto.copy()
            for name, data in import_payload["data"]["crypto_services"].items():
                if name not in merged_crypto:
                    merged_crypto[name] = data
                    imported_crypto += 1
                # Note: If name exists, we keep the existing one.
                # (Conflict resolution UI will be added in Phase 2)
            crypto_to_write = get_fernet().encrypt(json.dumps(merged_crypto).encode())
            
        # 3. Prepare Vault (MERGE Logic - FIXED)
        if "vault_text" in import_payload["data"]:
            # Parse existing vault
            existing_vault_data = []
            if os.path.exists(VAULT_FILE):
                try:
                    with open(VAULT_FILE, "rb") as vf:
                        v_encrypted = vf.read()
                    v_decrypted = get_fernet().decrypt(v_encrypted).decode()
                    reader = csv.reader(io.StringIO(v_decrypted.strip()))
                    next(reader, None) # Skip header
                    for row in reader:
                        if len(row) >= 2:
                            existing_vault_data.append(tuple(row))
                except Exception:
                    pass # If vault is corrupted/empty, start fresh
            
            # Parse backup vault
            backup_vault_data = []
            reader = csv.reader(io.StringIO(import_payload["data"]["vault_text"].strip()))
            next(reader, None) # Skip header
            for row in reader:
                if len(row) >= 2:
                    backup_vault_data.append(tuple(row))
            
            # Merge based on (service, password)
            merged_vault_data = existing_vault_data.copy()
            existing_keys = [(r[0], r[1]) for r in existing_vault_data]
            
            for row in backup_vault_data:
                if (row[0], row[1]) not in existing_keys:
                    merged_vault_data.append(row)
                    vault_merged_count += 1
            
            # Write merged vault to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["service", "password", "note"])
            writer.writerows(merged_vault_data)
            vault_to_write = get_fernet().encrypt(output.getvalue().encode())

        # 4. Transactional Write (With safer cleanup)
        paths = {
            "profiles": (PROFILES_FILE, profiles_to_write),
            "crypto": (CRYPTO_SERVICES_FILE, crypto_to_write),
            "vault": (VAULT_FILE, vault_to_write)
        }

        temp_files = {}
        bak_files = {}
        existed_before = {} 

        try:
            for k, (dest, data_bytes) in paths.items():
                existed_before[k] = os.path.exists(dest)
                if data_bytes:
                    temp_path = dest + f".tmp_{k}"
                    bak_path = dest + f".bak_{k}"
                    with open(temp_path, "wb") as f:
                        f.write(data_bytes)
                    temp_files[k] = temp_path
                    bak_files[k] = bak_path

            for k, (dest, _) in paths.items():
                if k in temp_files and existed_before[k]:
                    os.replace(dest, bak_files[k])

            for k, temp_path in temp_files.items():
                dest = paths[k][0]
                os.replace(temp_path, dest)

            # Success: cleanup backups
            for k, bak_path in bak_files.items():
                if os.path.exists(bak_path):
                    os.remove(bak_path)

            data_manager.invalidate_cache()
            crypto_data_manager.invalidate_cache()

        except Exception as e:
            # Rollback
            for k, temp_path in temp_files.items():
                if os.path.exists(temp_path): os.remove(temp_path)

            for k, (dest, _) in paths.items():
                if k in temp_files:
                    if existed_before[k] and os.path.exists(bak_files[k]):
                        if os.path.exists(dest): os.remove(dest)
                        os.replace(bak_files[k], dest)
                    elif not existed_before[k] and os.path.exists(dest):
                        os.remove(dest)

            return False, f"Import failed during write. Existing data was preserved.\nDetails: {e}"
        
        # 5. Accurate Summary Message
        summary_lines = []
        if imported_profiles > 0: summary_lines.append(f"{imported_profiles} new profiles added.")
        if imported_crypto > 0: summary_lines.append(f"{imported_crypto} new crypto services added.")
        if vault_merged_count > 0: summary_lines.append(f"{vault_merged_count} new passwords merged into Vault.")
        
        if not summary_lines:
            return True, "Import completed. All data in the backup already exists in your database."
            
        return True, "Import completed successfully!\n\n" + "\n".join(summary_lines)
    
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
    tk.Radiobutton(export_window, text="Profiles & Crypto Services", variable=export_var, value="profiles").pack(anchor="w", padx=20)
    tk.Radiobutton(export_window, text="Vault Only (Saved Passwords)", variable=export_var, value="vault").pack(anchor="w", padx=20)
    tk.Radiobutton(export_window, text="All Data (Profiles + Crypto + Vault)", variable=export_var, value="all").pack(anchor="w", padx=20)
    
    tk.Label(export_window, text="Backup Password (Required for security):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    pw_entry = tk.Entry(export_window, width=40, show="*")
    pw_entry.pack(pady=2)
    
    warning_lbl = tk.Label(export_window, text="You MUST remember this password to import this file later.", font=("Helvetica", 8), fg="#CC3333")
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