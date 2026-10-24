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
    root = tk.Tk()
    app = SPGApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()