"""
Entry point for running the application with: python -m spg
"""

import os
import signal
import tkinter as tk
from .ui import SPGApp

# Prevent Ctrl+Z (SIGTSTP) from suspending the GUI app on Unix-like systems
if os.name == 'posix':
    try:
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    except Exception:
        pass

def main():
    # Use className to ensure Linux taskbar picks up the correct icon
    root = tk.Tk(className="ibijan-pass")
    app = SPGApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()