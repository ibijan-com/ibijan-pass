import tkinter as tk
from tkinter import messagebox, ttk

from .config import (
    APP_VERSION, APP_WEBSITE, PASSWORD_PATTERNS, DEFAULT_PATTERN,
    BRAND_PRIMARY, BRAND_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_NEUTRAL
)
from .crypto import is_master_set, save_master_hash, hash_password, verify_master
from .validators import validate_profile_name
from .storage import (
    data_manager, save_profile, delete_profile, load_profile,
    save_to_vault, get_vault_data
)
from .generator import build_password
from .clipboard import clipboard_manager
from .dialogs import verify_master_password_for_profile, show_file_locations, factory_reset
from .backup import show_export_dialog, show_import_dialog
from .help import show_comprehensive_help

class SPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"iBijan Pass v{APP_VERSION} - Smart Password Generator")
        self.root.minsize(650, 800)
        self.root.configure(bg="#FFFFFF")
        
        self.last_generated_password = ""
        self._setup_styles()
        self.check_authentication()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Primary.TButton", background=BRAND_PRIMARY, foreground="white", font=("Arial", 10, "bold"), padding=5)
        style.map("Primary.TButton", background=[("active", BRAND_DARK)])
        
        style.configure("Success.TButton", background=COLOR_SUCCESS, foreground="white", font=("Arial", 10, "bold"), padding=5)
        style.map("Success.TButton", background=[("active", "#008a7b")])
        
        style.configure("Danger.TButton", background=COLOR_DANGER, foreground="white", font=("Arial", 10, "bold"), padding=5)
        style.map("Danger.TButton", background=[("active", "#a32929")])

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================
    # Authentication Flow
    # ==========================================
    def check_authentication(self):
        self.clear_screen()
        if is_master_set():
            self.show_login_screen()
        else:
            self.show_setup_screen()

    def show_login_screen(self):
        tk.Label(self.root, text="🔐 iBijan Pass", font=("Arial", 24, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(pady=(80, 5))
        tk.Label(self.root, text="Smart Password Generator", font=("Arial", 12), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(pady=(0, 40))
        
        tk.Label(self.root, text="Enter your master password", font=("Arial", 11), bg="#FFFFFF").pack(pady=10)
        
        self.login_entry = tk.Entry(self.root, show="*", width=28, font=("Arial", 14), justify="center")
        self.login_entry.pack(pady=10, ipady=5)
        self.login_entry.focus()
        
        ttk.Button(self.root, text="🔓 Unlock", style="Primary.TButton", command=self.authenticate).pack(pady=20, ipadx=30, ipady=5)
        self.login_entry.bind("<Return>", lambda e: self.authenticate())
        
        tk.Label(self.root, text=f"v{APP_VERSION} • {APP_WEBSITE}", font=("Arial", 8), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(side="bottom", pady=15)

    def authenticate(self):
        if verify_master(self.login_entry.get()):
            self.show_main_app()
        else:
            messagebox.showerror("Access Denied", "Incorrect master password.")
            self.login_entry.delete(0, tk.END)
            self.login_entry.focus()

    def show_setup_screen(self):
        tk.Label(self.root, text="🔐 Create Master Password", font=("Arial", 20, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(pady=(80, 30))
        
        tk.Label(self.root, text="Master Password:", bg="#FFFFFF").pack()
        self.pw1_entry = tk.Entry(self.root, show="*", width=30, font=("Arial", 12), justify="center")
        self.pw1_entry.pack(pady=5)
        
        tk.Label(self.root, text="Confirm Password:", bg="#FFFFFF").pack(pady=(10, 0))
        self.pw2_entry = tk.Entry(self.root, show="*", width=30, font=("Arial", 12), justify="center")
        self.pw2_entry.pack(pady=5)

        def create_master():
            pw1, pw2 = self.pw1_entry.get(), self.pw2_entry.get()
            if not pw1 or not pw2:
                messagebox.showerror("Error", "Please fill in both fields.")
                return
            if pw1 != pw2:
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return
            save_master_hash(hash_password(pw1))
            messagebox.showinfo("Success", "Master password set!\n\n⚠️ WARNING: If you forget this password, it cannot be recovered.")
            self.show_main_app()

        ttk.Button(self.root, text="Set Master Password", style="Success.TButton", command=create_master).pack(pady=25, ipadx=20, ipady=5)

    # ==========================================
    # Main Application UI
    # ==========================================
    def show_main_app(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#FFFFFF", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Header with Help button
        header_frame = tk.Frame(main_frame, bg="#FFFFFF")
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text="🔐 iBijan Pass", font=("Arial", 16, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(side="left")
        ttk.Button(header_frame, text="📚 Help Guide", command=lambda: show_comprehensive_help(self.root)).pack(side="right")

        # 1. Profile Section
        profile_frame = tk.LabelFrame(main_frame, text=" 📁 Password Profiles ", font=("Arial", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        profile_frame.pack(fill="x", pady=(0, 15))

        tk.Label(profile_frame, text="Select:", bg="#FFFFFF").grid(row=0, column=0, padx=5, pady=10)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var, width=30, state="readonly")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=10)
        self.update_profile_combo()
        
        ttk.Button(profile_frame, text="📥 Load", command=self.load_selected_profile).grid(row=0, column=2, padx=2)
        ttk.Button(profile_frame, text="🗑️ Delete", style="Danger.TButton", command=self.delete_selected_profile).grid(row=0, column=3, padx=2)

        # 2. Settings Section
        settings_frame = tk.LabelFrame(main_frame, text=" 🔧 Password Settings ", font=("Arial", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        settings_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(settings_frame, text="New Profile Name:", bg="#FFFFFF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.profile_name_entry = tk.Entry(settings_frame, width=25)
        self.profile_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(settings_frame, text="💾 Save As New", style="Success.TButton", command=self.save_current_profile).grid(row=0, column=2, padx=10)

        self.require_master_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_frame, text="🔒 Require Master Password to load this profile", variable=self.require_master_var, bg="#FFFFFF").grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        tk.Label(settings_frame, text="Prefix:", bg="#FFFFFF").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.prefix_entry = tk.Entry(settings_frame, width=25)
        self.prefix_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Base Number:", bg="#FFFFFF").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.base_entry = tk.Entry(settings_frame, width=25)
        self.base_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Special Characters:", bg="#FFFFFF").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.special_entry = tk.Entry(settings_frame, width=25)
        self.special_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Service Name:", bg="#FFFFFF").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.service_entry = tk.Entry(settings_frame, width=25)
        self.service_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.service_entry.bind("<Return>", lambda e: self.generate_password())

        tk.Label(settings_frame, text="Capitalize Letter:", bg="#FFFFFF").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.capitalize_entry = tk.Entry(settings_frame, width=25)
        self.capitalize_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Quotation:", bg="#FFFFFF").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.quotation_var = tk.StringVar(value="single")
        q_frame = tk.Frame(settings_frame, bg="#FFFFFF")
        q_frame.grid(row=7, column=1, sticky="w")
        tk.Radiobutton(q_frame, text="None", variable=self.quotation_var, value="none", bg="#FFFFFF").pack(side="left")
        tk.Radiobutton(q_frame, text="Single ( ' )", variable=self.quotation_var, value="single", bg="#FFFFFF").pack(side="left")
        tk.Radiobutton(q_frame, text="Double ( \" )", variable=self.quotation_var, value="double", bg="#FFFFFF").pack(side="left")

        tk.Label(settings_frame, text="Pattern:", bg="#FFFFFF").grid(row=8, column=0, sticky="w", padx=5, pady=10)
        self.pattern_var = tk.StringVar(value=DEFAULT_PATTERN)
        ttk.Combobox(settings_frame, textvariable=self.pattern_var, values=list(PASSWORD_PATTERNS.keys()), width=40, state="readonly").grid(row=8, column=1, columnspan=2, sticky="w", padx=5)

        # 3. Action Buttons
        action_frame = tk.Frame(main_frame, bg="#FFFFFF")
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="🔐 Generate", style="Primary.TButton", command=self.generate_password).pack(side="left", padx=(0, 10), ipadx=10, ipady=5)
        ttk.Button(action_frame, text="💾 Save to Vault", style="Success.TButton", command=self.save_to_vault).pack(side="left", padx=5)
        ttk.Button(action_frame, text="📋 View Vault", command=self.view_vault).pack(side="left", padx=5)

        # 4. Data Transfer (Import/Export)
        data_frame = tk.LabelFrame(main_frame, text=" 🔄 Data Transfer ", font=("Arial", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        data_frame.pack(fill="x", pady=10)
        
        btn_frame = tk.Frame(data_frame, bg="#FFFFFF")
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="📤 Export", style="Success.TButton", command=lambda: show_export_dialog(self.root)).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="📥 Import", style="Primary.TButton", command=lambda: show_import_dialog(self.root, self.update_profile_combo)).pack(side="left", padx=10)

        # 5. Bottom Danger Zone
        bottom_frame = tk.Frame(main_frame, bg="#FFFFFF")
        bottom_frame.pack(fill="x", side="bottom", pady=10)
        
        ttk.Button(bottom_frame, text="📍 File Locations", command=lambda: show_file_locations(self.root)).pack(side="left")
        ttk.Button(bottom_frame, text="🔥 Factory Reset", style="Danger.TButton", command=lambda: factory_reset(self.root, self.root.destroy)).pack(side="right")

    # ==========================================
    # Logical Handlers
    # ==========================================
    def update_profile_combo(self):
        profiles = data_manager.get_profiles()
        display_names = [f"🔒 {name}" if data.get("require_master") else f"📁 {name}" for name, data in profiles.items()]
        self.profile_combo['values'] = display_names

    def load_selected_profile(self):
        display_name = self.profile_var.get()
        if not display_name:
            return
        profile_name = display_name.replace("🔒 ", "").replace("📁 ", "")
        profile_data = load_profile(profile_name)
        
        if profile_data:
            if profile_data.get("require_master") and not verify_master_password_for_profile(self.root):
                return
            
            self.prefix_entry.delete(0, tk.END); self.prefix_entry.insert(0, profile_data.get("prefix", ""))
            self.base_entry.delete(0, tk.END); self.base_entry.insert(0, profile_data.get("base_number", ""))
            self.special_entry.delete(0, tk.END); self.special_entry.insert(0, profile_data.get("special_chars", ""))
            self.capitalize_entry.delete(0, tk.END); self.capitalize_entry.insert(0, profile_data.get("capitalize_letter", ""))
            self.quotation_var.set(profile_data.get("quotation_style", "single"))
            self.pattern_var.set(profile_data.get("password_pattern", DEFAULT_PATTERN))
            messagebox.showinfo("Loaded", f"Profile '{profile_name}' loaded.", parent=self.root)

    def save_current_profile(self):
        name = self.profile_name_entry.get().strip() or f"Profile_{len(data_manager.get_profiles()) + 1}"
        success, msg = save_profile(
            name, self.prefix_entry.get(), self.base_entry.get(), self.special_entry.get(),
            self.capitalize_entry.get(), self.quotation_var.get(), self.pattern_var.get(),
            self.require_master_var.get()
        )
        if success:
            messagebox.showinfo("Success", msg, parent=self.root)
            self.update_profile_combo()
            self.profile_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg, parent=self.root)

    def delete_selected_profile(self):
        display_name = self.profile_var.get()
        if not display_name: return
        name = display_name.replace("🔒 ", "").replace("📁 ", "")
        if messagebox.askyesno("Confirm", f"Delete profile '{name}'?", parent=self.root):
            if delete_profile(name):
                self.update_profile_combo()
                self.profile_var.set("")

    def generate_password(self):
        pw, warning = build_password(
            self.prefix_entry.get(), self.base_entry.get(), self.special_entry.get(),
            self.service_entry.get(), self.capitalize_entry.get(),
            self.quotation_var.get(), self.pattern_var.get()
        )
        
        if warning: messagebox.showwarning("Warning", warning, parent=self.root)
            
        if pw:
            if clipboard_manager.copy_to_clipboard(pw):
                messagebox.showinfo("Generated", f"Password copied to clipboard:\n{pw}", parent=self.root)
            else:
                messagebox.showinfo("Generated", f"Password (copy manually):\n{pw}", parent=self.root)
            self.last_generated_password = pw

    def save_to_vault(self):
        svc = self.service_entry.get()
        if not svc or not self.last_generated_password:
            messagebox.showerror("Error", "Generate a password first!", parent=self.root)
            return
        success, msg = save_to_vault(svc, self.last_generated_password)
        if success: messagebox.showinfo("Success", msg, parent=self.root)
        else: messagebox.showerror("Error", msg, parent=self.root)

    def view_vault(self):
        vault_text = get_vault_data()
        if not vault_text:
            messagebox.showinfo("Vault Empty", "No saved passwords.", parent=self.root)
            return
        
        vw = tk.Toplevel(self.root)
        vw.title("Saved Passwords")
        vw.geometry("400x300")
        text = tk.Text(vw, wrap="word")
        text.insert("1.0", vault_text)
        text.pack(expand=True, fill="both", padx=10, pady=10)