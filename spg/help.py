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
        "🚀 Mental Mode": """
1. Enter a Prefix (Letters only, e.g., BI).
2. Enter a Base Number (Numbers only, e.g., 100).
3. Add Special Characters (e.g., @).
4. Enter Service Name (e.g., gmail).
5. (Optional) Enter a Capitalize Letter(s) (up to 3 letters, e.g., G).
6. Click "Generate".

How the math works (Example: gmail, Base 100, Letter G):
• Service "gmail" has 5 letters.
• Capitalize letter: G.
• Middle part = Length (5) + Letter (G) = "5G"
• End number = Base (100) + Length (5) = 105
• Final Password (Default pattern) = BI + 5G + @ + 105 = BI5G@105

Note: If you leave the Capitalize Letter empty, the password will not have uppercase letters.
""",
        "🔐 Cryptographic Mode": """
Cryptographic Mode generates highly secure, random-looking passwords based on a Master Secret and the Service Name. It does NOT save the generated passwords.

How to use:
1. Enter your Master Secret. (This is different from your Application Master Password. Keep it safe!)
2. Enter the Service Name (e.g., google) and Account/Username (e.g., user@gmail.com).
3. Choose your desired Password Length (4 to 128 characters).
4. Select character types (Uppercase, Lowercase, Digits, Symbols).
5. Click "Generate".

How it works:
• The password is generated mathematically using your Master Secret and a unique random "Salt" generated for that specific service.
• If you use the same Master Secret and Service details on ANOTHER computer, the password will be EXACTLY the same.
• You can save the service settings (without the password) using the "Save Service" button for quick access.
""",
        "🎨 Arrangement Patterns": """
Mental Mode allows you to choose how your password is built:

• PREFIX: The fixed text you defined (e.g., BI).
• MIDDLE: The length of the service name + the Capital letter you provided. 
• SPECIAL: Your chosen symbols (e.g., @).
• END_NUMBER: Your Base Number + the length of the service name. 

Available Patterns:
1. PREFIX + MIDDLE + SPECIAL + END_NUMBER (BI5G@105)
2. END_NUMBER + MIDDLE + SPECIAL + PREFIX (1055G@BI)
3. SPECIAL + PREFIX + MIDDLE + END_NUMBER (@BI5G105)
4. MIDDLE + END_NUMBER + PREFIX + SPECIAL (5G105BI@)
5. PREFIX + SPECIAL + MIDDLE + END_NUMBER (BI@5G105)
6. END_NUMBER + SPECIAL + PREFIX + MIDDLE (105@BI5G)
""",
        "💾 Backup & Restore": """
The Export/Import feature ensures you never lose your data. All backups are saved as .ibpass files.

• Export:
  - Select "Profiles & Crypto Services" to backup your patterns and saved service settings.
  - Select "Vault Only" to backup your saved passwords.
  - Select "All Data" for a complete backup.
  - IMPORTANT: You MUST set a Backup Password. This encrypts the file securely.

• Import:
  - Select the backup file, enter the Backup Password, and your data will be restored.
  - If restoring a Vault, it will replace your current Vault. (Profiles and Crypto Services are merged safely).

• Important Note: If you lose your Backup Password, the file cannot be recovered.
""",
        "🔧 Troubleshooting": """
• Clipboard not working on Linux? 
  Run: sudo apt install xclip

• Forgot Application Master Password?
  Click "Forgot Master Password?" on the login screen. This will trigger a Factory Reset, which deletes ALL local data. You can then restore your data using an .ibpass backup file.

• "Critical Security Error" on startup?
  This means the encryption key is missing but data exists. The app prevents you from accidentally overwriting your data.
"""
    }
    
    for title, content in tabs.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        
        text_widget = tk.Text(frame, wrap="word", padx=15, pady=15, font=("Helvetica", 12))
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