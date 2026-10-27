import os
import sys
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

from .config import (
    CONFIG_DIR, KEY_FILE, MASTER_HASH_FILE, VAULT_FILE, 
    PROFILES_FILE, APP_VERSION, APP_WEBSITE
)
# CORRECTED IMPORT: Using the new verify_master_password function
from .crypto import verify_master_password
from .clipboard import clipboard_manager


def show_custom_error(root, title, message):
    """Custom error dialog to prevent window resizing."""
    err_win = tk.Toplevel(root)
    err_win.title(title)
    err_win.transient(root)
    err_win.grab_set()
    err_win.resizable(False, False)
    
    # Calculate dynamic size based on message length
    lines = message.count('\n') + 1
    height = max(200, 100 + (lines * 20))
    err_win.geometry(f"400x{height}")

    tk.Label(err_win, text="🔴", font=("Helvetica", 24)).pack(pady=(15, 5))
    tk.Label(err_win, text=title, font=("Helvetica", 12, "bold")).pack(pady=5)
    
    msg_label = tk.Label(err_win, text=message, font=("Helvetica", 10), wraplength=350, justify="center")
    msg_label.pack(pady=10, padx=20)
    
    tk.Button(err_win, text="OK", command=err_win.destroy, width=10, bg="#1C39BB", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)

    err_win.update_idletasks()
    x = (err_win.winfo_screenwidth() // 2) - (err_win.winfo_width() // 2)
    y = (err_win.winfo_screenheight() // 2) - (err_win.winfo_height() // 2)
    err_win.geometry(f"+{x}+{y}")


def verify_master_password_for_profile(root) -> bool:
    verify_window = tk.Toplevel(root)
    verify_window.title("Master Password Required")
    verify_window.geometry("350x180")
    verify_window.transient(root)
    verify_window.grab_set()
    verify_window.resizable(False, False)

    tk.Label(verify_window, text="🔒 Master Password Required", font=("Helvetica", 12, "bold")).pack(pady=10)
    tk.Label(verify_window, text="This secure profile requires additional authentication:", font=("Helvetica", 9)).pack(pady=5)

    password_entry = tk.Entry(verify_window, show="*", width=25, font=("Helvetica", 10))
    password_entry.pack(pady=15)
    password_entry.focus()

    result = [False]

    def check_password():
        # CORRECTED: Using the new verify function
        if verify_master_password(password_entry.get()):
            result[0] = True
            verify_window.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect master password!", parent=verify_window)
            password_entry.delete(0, tk.END)
            password_entry.focus()

    btn_frame = tk.Frame(verify_window)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Verify", command=check_password, width=10, bg="#00A693", fg="white").pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", command=verify_window.destroy, width=10, bg="#CC3333", fg="white").pack(side="left", padx=5)

    password_entry.bind("<Return>", lambda e: check_password())
    verify_window.wait_window()
    return result[0]


def show_file_locations(root):
    locations_window = tk.Toplevel(root)
    locations_window.title("File Locations - iBijan Pass")
    locations_window.geometry("650x450")
    locations_window.minsize(600, 400)

    button_frame = tk.Frame(locations_window)
    button_frame.pack(side="bottom", fill="x", pady=10)

    text_frame = tk.Frame(locations_window)
    text_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 0))

    content = f"""
📁 Current File Locations on Your System:

🔧 Config Directory:
{CONFIG_DIR}

💾 Profile File (Encrypted):
{PROFILES_FILE}

🔐 Vault File (Encrypted):
{VAULT_FILE}

🗝️ Encryption Key:
{KEY_FILE}

🔑 Master Password Hash:
{MASTER_HASH_FILE}

📊 Status:
• Config directory exists: {os.path.exists(CONFIG_DIR)}
• Profiles file exists: {os.path.exists(PROFILES_FILE)}
• Vault file exists: {os.path.exists(VAULT_FILE)}
• Master password set: {os.path.exists(MASTER_HASH_FILE)}

💡 Important Information:
• These paths are automatically created based on your system username
• Each user has unique file locations
• Files are encrypted for security
"""
    text_widget = tk.Text(text_frame, wrap="word", padx=10, pady=10, font=("Helvetica", 10))
    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")

    def copy_all_paths():
        all_paths = f"Config: {CONFIG_DIR}\nVault: {VAULT_FILE}\nProfiles: {PROFILES_FILE}"
        clipboard_manager.copy_to_clipboard(all_paths)
        messagebox.showinfo("Copied", "File paths copied to clipboard!", parent=locations_window)

    tk.Button(button_frame, text="Copy All Paths", command=copy_all_paths, bg="#1C39BB", fg="white", width=15).pack(side="left", padx=20)
    tk.Button(button_frame, text="Close", command=locations_window.destroy, bg="#CC3333", fg="white", width=15).pack(side="right", padx=20)


def factory_reset(root, on_complete_callback=None):
    confirm1 = messagebox.askyesno(
        "⚠️ STAGE 1 - Serious Warning",
        "Are you sure you want to delete ALL data?\n\n"
        "This action is PERMANENT and IRREVERSIBLE!\n\n"
        "✅ What will be deleted:\n"
        "• All saved password profiles\n"
        "• All passwords in vault\n"
        "• Master password\n"
        "• Encryption keys\n",
        parent=root
    )
    if not confirm1:
        return

    confirm_window = tk.Toplevel(root)
    confirm_window.title("Final Confirmation")
    confirm_window.geometry("450x250")
    confirm_window.transient(root)
    confirm_window.grab_set()
    confirm_window.resizable(False, False)

    tk.Label(confirm_window, text="⚠️ FINAL CONFIRMATION REQUIRED", font=("Helvetica", 12, "bold"), fg="#CC3333").pack(pady=10)
    tk.Label(confirm_window, text="To permanently delete ALL data, please type the following phrase:\n\"DELETE ALL DATA\"", font=("Helvetica", 10), justify="center").pack(pady=5)

    confirmation_entry = tk.Entry(confirm_window, width=30, font=("Helvetica", 10), justify="center")
    confirmation_entry.pack(pady=15)
    confirmation_entry.focus()

    def final_confirmation():
        if confirmation_entry.get() == "DELETE ALL DATA":
            confirm_window.destroy()
            _perform_factory_reset(root, on_complete_callback)
        else:
            messagebox.showerror("Error", "The phrase you entered is incorrect!", parent=confirm_window)

    confirmation_entry.bind("<Return>", lambda e: final_confirmation())

    button_frame = tk.Frame(confirm_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="CONFIRM DELETE", command=final_confirmation, bg="#CC3333", fg="white", font=("Helvetica", 10, "bold"), width=15).pack(side="left", padx=5)
    tk.Button(button_frame, text="CANCEL", command=confirm_window.destroy, bg="#6B7280", fg="white", width=10).pack(side="left", padx=5)


def _perform_factory_reset(root, on_complete_callback):
    files_to_delete = [VAULT_FILE, PROFILES_FILE, MASTER_HASH_FILE, KEY_FILE]
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    try:
        if os.path.exists(CONFIG_DIR) and not os.listdir(CONFIG_DIR):
            os.rmdir(CONFIG_DIR)
    except Exception:
        pass

    messagebox.showinfo("Factory Reset Complete", "✅ Factory reset completed successfully!\nThe application will now restart.", parent=root)
    
    # Restart the application
    root.destroy()
    os.execl(sys.executable, sys.executable, *sys.argv)


def open_config_folder(root):
    try:
        if os.name == 'nt':
            os.startfile(CONFIG_DIR)
        elif os.uname().sysname == 'Darwin':
            subprocess.run(["open", CONFIG_DIR])
        else:
            subprocess.run(["xdg-open", CONFIG_DIR])
    except Exception as e:
        show_custom_error(root, "Error", f"Could not open folder:\n{e}")


def show_about_dialog(root):
    about_window = tk.Toplevel(root)
    about_window.title("About iBijan Pass")
    about_window.geometry("400x380")
    about_window.transient(root)
    about_window.grab_set()
    about_window.resizable(False, False)

    tk.Label(about_window, text="🔐 iBijan Pass", font=("Helvetica", 18, "bold"), fg="#1C39BB").pack(pady=(20, 5))
    tk.Label(about_window, text="Memorable Password Generation", font=("Helvetica", 11), fg="gray").pack()
    tk.Label(about_window, text=f"Version: {APP_VERSION}", font=("Helvetica", 9)).pack(pady=(5, 15))
    tk.Label(about_window, text="An offline, encrypted password generator\nwith custom patterns and vault storage.", justify="center").pack()

    link_frame = tk.Frame(about_window)
    link_frame.pack(pady=15)

    def open_url(url):
        webbrowser.open_new(url)

    web_link = tk.Label(link_frame, text="🌐 Website: ibijan.com", fg="#1C39BB", cursor="hand2", font=("Helvetica", 10, "underline"))
    web_link.pack()
    web_link.bind("<Button-1>", lambda e: open_url(APP_WEBSITE))

    gh_link = tk.Label(link_frame, text="🐙 GitHub: ibijan-com/ibijan-pass", fg="#1C39BB", cursor="hand2", font=("Helvetica", 10, "underline"))
    gh_link.pack(pady=5)
    gh_link.bind("<Button-1>", lambda e: open_url("https://github.com/ibijan-com/ibijan-pass"))

    tk.Label(about_window, text="License: MIT", font=("Helvetica", 9), fg="gray").pack(pady=(10, 5))
    tk.Label(about_window, text="© 2024 IbiJan", font=("Helvetica", 9), fg="gray").pack()

    tk.Button(about_window, text="Close", command=about_window.destroy, bg="#CC3333", fg="white", width=10, font=("Helvetica", 10, "bold")).pack(side="bottom", pady=15)