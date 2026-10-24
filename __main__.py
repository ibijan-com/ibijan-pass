"""
Entry point for running the application with: python -m spg
"""

import tkinter as tk
from .ui import SPGApp

def main():
    root = tk.Tk()
    app = SPGApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
