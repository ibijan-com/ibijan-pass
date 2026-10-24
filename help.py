import tkinter as tk
from tkinter import ttk
from .config import APP_VERSION, APP_WEBSITE

def show_comprehensive_help(root):
    help_window = tk.Toplevel(root)
    help_window.title(f"📚 Guide - iBijan Pass v{APP_VERSION}")
    help_window.geometry("700x600")
    help_window.minsize(650, 500)
    
    notebook = ttk.Notebook(help_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    tabs = {
        "🚀 Quick Start": """
1. Enter a Prefix (e.g., BI)
2. Enter a Base Number (e.g., 100)
3. Add Special Characters (e.g., @)
4. Enter Service Name (e.g., gmail)
5. Click "Generate Password"

Your password will be copied to the clipboard automatically!
You can save your settings as a Profile for later use.
""",
        "🎨 Patterns": """
You can choose how your password is built.
Components:
• PREFIX: User-defined text
• MIDDLE: Service length + Capital letter
• SPECIAL: Your chosen symbols
• END_NUMBER: Base number + Service length

Example for 'gmail' (length 5) with Base 100:
PREFIX (BI) + MIDDLE (5G) + SPECIAL (@) + END (105)
Result: BI5G@105
""",
        "🔒 Security": """
• Master Password: Encrypts all your data. Cannot be recovered if lost.
• Secure Profiles (🔒): Require the master password every time you load them. Great for Banking or Email.
• Normal Profiles (📁): Load instantly without prompts.
• Vault: All saved passwords are encrypted using AES-128.
""",
        "💾 Backup": """
• Export Data: Saves your profiles and vault to a .spg file.
• Advanced Security: You can encrypt the backup with a separate key.
• Import Data: Restores your data. Existing profiles with the same name will NOT be overwritten.
""",
        "🔧 Troubleshooting": """
• Clipboard not working on Linux? 
  Run: sudo apt install xclip

• Forgot Master Password?
  You must use Factory Reset. All data will be lost.

• Lost your Import Key?
  The backup file cannot be decrypted.
"""
    }
    
    for title, content in tabs.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        
        text_widget = tk.Text(frame, wrap="word", padx=15, pady=15, font=("Arial", 12))
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        text_widget.insert("1.0", content.strip())
        text_widget.config(state="disabled")
        
    tk.Button(help_window, text="Close", command=help_window.destroy, bg="#CC3333", fg="white", width=10).pack(pady=10)
