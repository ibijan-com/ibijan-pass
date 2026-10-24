"""
Clipboard management and UI tooltips for SPG.

Provides cross-platform clipboard functionality (Linux, macOS, Windows)
and a simple ToolTip class for Tkinter widgets.
"""

import subprocess
import tkinter as tk
from tkinter import messagebox


class ClipboardManager:
    def __init__(self):
        self.methods = [
            self._try_xclip,
            self._try_pbcopy,
            self._try_tkinter,
        ]

    def copy_to_clipboard(self, text: str) -> bool:
        for method in self.methods:
            try:
                if method(text):
                    print(f"✓ Clipboard method successful: {method.__name__}")
                    return True
            except Exception as e:
                print(f"✗ Clipboard method failed {method.__name__}: {e}")

        messagebox.showerror("Clipboard Error",
                             "Could not copy to clipboard using any method.\n"
                             "Please copy manually:\n\n" + text)
        return False

    def _try_xclip(self, text: str) -> bool:
        try:
            result = subprocess.run(["which", "xclip"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            subprocess.run(["xclip", "-selection", "clipboard"],
                           input=text.encode(), check=True, timeout=5)
            return True
        except Exception:
            return False

    def _try_pbcopy(self, text: str) -> bool:
        try:
            result = subprocess.run(["which", "pbcopy"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            subprocess.run("pbcopy", input=text.encode(), check=True, shell=True, timeout=5)
            return True
        except Exception:
            return False

    def _try_tkinter(self, text: str) -> bool:
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.clipboard_clear()
            temp_root.clipboard_append(text)
            temp_root.update()
            temp_root.destroy()
            return True
        except Exception:
            return False


# Singleton instance
clipboard_manager = ClipboardManager()


def detect_clipboard_method() -> str:
    """Returns a string describing the active clipboard method for the status bar."""
    try:
        if subprocess.run(["which", "xclip"], capture_output=True).returncode == 0:
            return "xclip (Linux)"
    except Exception:
        pass

    try:
        if subprocess.run(["which", "pbcopy"], capture_output=True).returncode == 0:
            return "pbcopy (macOS)"
    except Exception:
        pass

    return "tkinter (fallback)"


class ToolTip:
    """Creates a floating tooltip when hovering over a widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)
        widget.bind("<Motion>", self.motion)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def motion(self, event=None):
        self.x, self.y = event.x, event.y

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show_tip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + self.x + 25
        y = self.widget.winfo_rooty() + self.y + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("Arial", 10))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
