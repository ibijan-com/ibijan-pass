import tkinter as tk
from tkinter import ttk
from .config import APP_VERSION

# Global variable to track the help window instance
_help_window = None

def show_comprehensive_help(root):
    global _help_window
    
    # Check if the window is already open and exists
    if _help_window is not None and _help_window.winfo_exists():
        _help_window.lift()
        _help_window.focus_force()
        return

    _help_window = tk.Toplevel(root)
    _help_window.title(f"📚 Guide - iBijan Pass v{APP_VERSION}")
    _help_window.geometry("800x650")
    _help_window.minsize(750, 550)
    
    button_frame = tk.Frame(_help_window)
    button_frame.pack(side="bottom", fill="x", pady=10)
    
    notebook = ttk.Notebook(_help_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))
    
    tabs = {
        "📖 Overview": """
Welcome to iBijan Pass!
iBijan Pass is a dual-mode password generator designed to keep you secure while remaining completely offline.

What is Mental Mode?
Mental Mode is designed around how the human brain remembers things. Instead of remembering random characters, you remember a "formula" or "pattern" (e.g., a Prefix, a Base Number, and Special Characters). When you need a password for a specific service (like Google), you apply your pattern to the service name. It is highly memorable but relies on the secrecy of your pattern.

What is Cryptographic Mode?
Cryptographic Mode is for users who want mathematically random, highly secure passwords. You only need to remember one "Master Secret". The application uses this secret and the service name to generate a highly complex password. It does not rely on a memorable pattern, but it is deterministic (the same inputs always generate the exact same password).

Main Menu Bar:
- File: Export/Import backups, Open Config Folder, and view File Locations.
- Tools: Clear the Vault or perform a Factory Reset.
- Help: Open this guide or view the About screen.
""",
        "🧠 Mental Mode": """
Mental Mode allows you to generate passwords using a repeatable personal pattern.

How to use:
1. Enter a Prefix (Letters only, e.g., BI).
2. Enter a Base Number (Numbers only, e.g., 100).
3. Add Special Characters (e.g., @).
4. Enter the Service Name (e.g., gmail).
5. (Optional) Enter Capitalize Letter(s) (up to 3 letters, e.g., G).
6. Click "Generate".

How the math works (Example: gmail, Base 100, Letter G):
• Service "gmail" has 5 letters.
• Capitalize letter: G.
• Middle part = Length (5) + Letter (G) = "5G"
• End number = Base (100) + Length (5) = 105
• Final Password (Default pattern) = BI + 5G + @ + 105 = BI5G@105

Security Tip: Never share your formula. If an attacker obtains multiple passwords generated from the same pattern, they may reverse-engineer your formula.
""",
        "🔐 Cryptographic Mode": """
Cryptographic Mode generates highly secure, random-looking passwords based on a Master Secret and the Service Name. It does NOT save the generated passwords to any database.

How to use:
1. Enter your Master Secret. (This is different from your Application Master Password. Keep it safe!)
2. Enter the Service Name (e.g., google) and Account/Username (e.g., user@gmail.com).
3. Choose your desired Password Length (4 to 128 characters).
4. Select character types (Uppercase, Lowercase, Digits, Symbols).
5. Click "Generate".

Privacy Feature:
By default, your Account/Username is masked in the Saved Services list (e.g., bij***@gmail.com) to prevent shoulder surfing. You can click the "Eye" icon next to the input field to reveal/hide it.

How it works:
• The password is generated mathematically using your Master Secret and a unique random "Salt" generated for that specific service.
• If you use the same Master Secret and Service details on ANOTHER computer (after importing your backup), the password will be EXACTLY the same.
• You must save the service settings using the "Save Service" button for quick access.
""",
        "💾 Backup & Vault": """
The Export/Import feature ensures you never lose your data. All backups are saved as .ibpass files.

• Export:
  - Go to File -> Export Data...
  - Select "Profiles & Crypto Services" to backup your patterns and saved service settings.
  - Select "Vault Only" to backup your saved passwords.
  - Select "All Data" for a complete backup.
  - IMPORTANT: You MUST set a Backup Password. This encrypts the file securely.

• Import:
  - Go to File -> Import Data...
  - Select the backup file, enter the Backup Password, and your data will be restored.
  - If restoring a Vault, it will replace your current Vault. (Profiles and Crypto Services are merged safely).

• Vault:
  - You can save generated passwords to the encrypted Vault using the "Save to Vault" button.
  - Access saved passwords via the "View Vault" button.
""",
        "🔧 Troubleshooting": """
• Clipboard not working on Linux? 
  Run: sudo apt install xclip

• Forgot Application Master Password?
  Click "Forgot Master Password?" on the login screen. This will trigger a Factory Reset, which deletes ALL local data. You can then restore your data using an .ibpass backup file.

• "Critical Security Error" on startup?
  This means the encryption key is missing but data exists. The app prevents you from accidentally overwriting your data. You must restore from a backup.

• Keybindings:
  - Ctrl+A: Select all text in the active input field.
"""
    }
    
    for title, content in tabs.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        
        text_widget = tk.Text(frame, wrap="word", padx=15, pady=15, font=("Helvetica", 11))
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        text_widget.insert("1.0", content.strip())
        text_widget.config(state="disabled")
        
    tk.Button(
        button_frame, 
        text="Close", 
        command=_help_window.destroy, 
        bg="#CC3333", fg="white", width=12, font=("Helvetica", 10, "bold")
    ).pack()