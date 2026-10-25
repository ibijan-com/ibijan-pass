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
    _help_window.geometry("750x650")
    _help_window.minsize(700, 550)
    
    button_frame = tk.Frame(_help_window)
    button_frame.pack(side="bottom", fill="x", pady=10)
    
    notebook = ttk.Notebook(_help_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))
    
    tabs = {
        "🚀 Quick Start": """
1. Enter a Prefix (Letters only, e.g., BI).
2. Enter a Base Number (Numbers only, e.g., 100).
3. Add Special Characters (e.g., @).
4. Enter Service Name (e.g., gmail).
5. (Optional) Enter a Capitalize Letter (e.g., G).
6. Click "Generate Password".

Your password will be copied to the clipboard automatically!
Click "Clear" to reset all fields and start over.

How the math works (Example: gmail, Base 100, Letter G):
• Service "gmail" has 5 letters.
• Capitalize letter: G (The letter you typed, converted to uppercase).
• Middle part = Length (5) + Letter (G) = "5G"
• End number = Base (100) + Length (5) = 105
• Final Password (Default pattern) = BI + 5G + @ + 105 = BI5G@105

Note: If you leave the Capitalize Letter empty, the password will not have uppercase letters, and you will receive a security warning.
""",
        "🎨 Patterns": """
You can choose how your password is built using components:

• PREFIX: The fixed text you defined (e.g., BI).
• MIDDLE: The length of the service name + the Capital letter you provided. 
  (For "gmail" which is 5 letters and letter G, MIDDLE is "5G").
• SPECIAL: Your chosen symbols (e.g., @).
• END_NUMBER: Your Base Number + the length of the service name. 
  (Base 100 + 5 letters = 105).

Available Arrangement Patterns:
1. PREFIX + MIDDLE + SPECIAL + END_NUMBER (BI5G@105)
2. END_NUMBER + MIDDLE + SPECIAL + PREFIX (1055G@BI)
3. SPECIAL + PREFIX + MIDDLE + END_NUMBER (@BI5G105)
4. MIDDLE + END_NUMBER + PREFIX + SPECIAL (5G105BI@)
5. PREFIX + SPECIAL + MIDDLE + END_NUMBER (BI@5G105)
6. END_NUMBER + SPECIAL + PREFIX + MIDDLE (105@BI5G)
""",
        "🔒 Vault & Security": """
• Master Password: Encrypts all your data. Cannot be recovered if lost.
• Secure Profiles (🔒): Require the master password every time you load them. Great for Banking or Email.
• Normal Profiles (📁): Load instantly without prompts.

💾 Password Vault:
• View Vault: Shows a table of your saved passwords.
• Note Column: You can add an optional note (e.g., "Work Email") when saving a password to help you remember it.
• Copying: Select any row in the Vault table and click "Copy Selected Password" to copy it securely to your clipboard.
• Clear Vault: Permanently deletes all saved passwords from your vault.
""",
        "💾 Backup": """
• Export Data: Saves your profiles and vault to a .spg file.
• Advanced Security: You can encrypt the backup with a separate key. If you do, you MUST keep that key safe, otherwise you cannot import the file!
• Import Data: Restores your data. Existing profiles with the same name will NOT be overwritten.
""",
        "🔧 Troubleshooting": """
• Clipboard not working on Linux? 
  Run: sudo apt install xclip

• Forgot Master Password?
  You must use Factory Reset. All data will be lost.

• Lost your Import Key?
  The backup file cannot be decrypted.

• Inputs not working?
  For security reasons, some fields are restricted (e.g., Base Number only accepts digits, Prefix only accepts letters).
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