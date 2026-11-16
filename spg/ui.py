import tkinter as tk
from tkinter import messagebox, ttk
import os

from .clipboard import clipboard_manager, ToolTip
from .config import (
    APP_VERSION, APP_WEBSITE, CONFIG_DIR, PASSWORD_PATTERNS, DEFAULT_PATTERN,
    BRAND_PRIMARY, BRAND_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_NEUTRAL
)
from .crypto import is_master_set, setup_master_password, verify_master_password, get_fernet, KeyIntegrityError, lock_fernet
from .validators import (
    validate_prefix, validate_base_number, validate_special_chars,
    validate_service_name, validate_capitalize_letter, validate_profile_name
)
from .storage import (
    data_manager, save_profile, delete_profile, load_profile,
    save_to_vault, get_vault_data, clear_vault, delete_from_vault
)
from .generator import build_password
from .crypto_generator import generate_crypto_password, generate_salt, encode_salt, decode_salt
from .crypto_storage import (
    crypto_data_manager, save_crypto_service, delete_crypto_service, load_crypto_service
)
from .dialogs import (
    verify_master_password_for_profile, show_file_locations, 
    factory_reset, open_config_folder, show_about_dialog
)
from .backup import show_export_dialog, show_import_dialog
from .help import show_comprehensive_help

# ==========================================
# Custom UI Component: Placeholder Entry
# ==========================================
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", color='gray', *args, **kwargs):
        self._validatecommand = kwargs.pop('validatecommand', None)
        super().__init__(master, *args, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, e=None):
        if self['fg'] == self.placeholder_color:
            self.config(validate="none")
            self.delete(0, "end")
            self.config(validate="key", validatecommand=self._validatecommand)
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        if not self.get():
            self.config(validate="none")
            self.insert(0, self.placeholder)
            self.config(validate="key", validatecommand=self._validatecommand)
            self['fg'] = self.placeholder_color
    
    def get_value(self):
        if self['fg'] == self.placeholder_color:
            return ""
        return self.get()

# ==========================================
# Main Application Class
# ==========================================
class SPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"iBijan Pass v{APP_VERSION} - Memorable Password Generation")
        self.root.minsize(700, 780) # Reduced from 880 to 780
        self.root.configure(bg="#FFFFFF")
        
        # FIXED: Set the window class for Linux taskbar matching
        
        # FIXED: Correctly locate the icon and KEEP A REFERENCE to it
        import sys
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(bundle_dir, "icon.png")
        if os.path.exists(icon_path):
            try:
                self.icon_img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, self.icon_img)
                # FIXED: Force update to apply the icon immediately
                self.root.update_idletasks()
            except Exception as e:
                print(f"Could not load icon: {e}")
                                        
        self.last_generated_password = ""
        self._setup_styles()

        self.root.bind_class("Entry", "<Control-a>", self._select_all)
        self.root.bind_class("Entry", "<Control-A>", self._select_all)
        self.root.bind_class("TEntry", "<Control-a>", self._select_all)
        self.root.bind_class("TEntry", "<Control-A>", self._select_all)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.check_authentication()

    def on_closing(self):
        lock_fernet()
        self.root.destroy()

    def _select_all(self, event):
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')
        return 'break'

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Primary.TButton", background=BRAND_PRIMARY, foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Primary.TButton", background=[("active", BRAND_DARK)])
        
        style.configure("Success.TButton", background=COLOR_SUCCESS, foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Success.TButton", background=[("active", "#008a7b")])
        
        style.configure("Danger.TButton", background=COLOR_DANGER, foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Danger.TButton", background=[("active", "#a32929")])

        style.configure("Neutral.TButton", background="#6B7280", foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Neutral.TButton", background=[("active", "#4B5563")])

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def check_authentication(self):
        self.clear_screen()
        try:
            if is_master_set():
                self.show_login_screen()
            else:
                self.show_setup_screen()
        except KeyIntegrityError as e:
            messagebox.showerror("Critical Security Error", str(e), parent=self.root)
            self.root.destroy()

    def show_login_screen(self):
        tk.Label(self.root, text="🔐 iBijan Pass", font=("Helvetica", 24, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(pady=(80, 5))
        tk.Label(self.root, text="Memorable Password Generation", font=("Helvetica", 12), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(pady=(0, 5))
        tk.Label(self.root, text="A personal-pattern approach to generating passwords.", font=("Helvetica", 9), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(pady=(0, 30))
        tk.Label(self.root, text="Enter your master password", font=("Helvetica", 11), bg="#FFFFFF").pack(pady=10)
        
        self.login_entry = tk.Entry(self.root, show="*", width=28, font=("Helvetica", 14), justify="center")
        self.login_entry.pack(pady=10, ipady=5)
        self.login_entry.focus()
        
        ttk.Button(self.root, text="🔓 Unlock", style="Primary.TButton", command=self.authenticate).pack(pady=(20, 10), ipadx=30, ipady=5)
        self.login_entry.bind("<Return>", lambda e: self.authenticate())
        
        # FIXED: Moved fg=COLOR_DANGER outside the font tuple
        forgot_btn = tk.Button(self.root, text="Forgot Master Password?", 
                               font=("Helvetica", 9), 
                               fg=COLOR_DANGER, 
                               bg="#FFFFFF", 
                               activebackground="#FFFFFF", 
                               relief="flat", 
                               cursor="hand2",
                               command=lambda: factory_reset(self.root, self.root.destroy))
        forgot_btn.pack(pady=5)
        
        tk.Label(self.root, text=f"v{APP_VERSION} • {APP_WEBSITE}", font=("Helvetica", 8), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(side="bottom", pady=15)
                
    def authenticate(self):
        password = self.login_entry.get()
        if verify_master_password(password):
            try:
                get_fernet()
                self.show_main_app()
            except KeyIntegrityError as e:
                messagebox.showerror("Critical Security Error", str(e), parent=self.root)
        else:
            messagebox.showerror("Access Denied", "Incorrect master password.", parent=self.root)
            self.login_entry.delete(0, tk.END)
            self.login_entry.focus()

    def show_setup_screen(self):
        tk.Label(self.root, text="🔐 Create Master Password", font=("Helvetica", 20, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(pady=(80, 30))
        tk.Label(self.root, text="Master Password:", bg="#FFFFFF").pack()
        self.pw1_entry = tk.Entry(self.root, show="*", width=30, font=("Helvetica", 12), justify="center")
        self.pw1_entry.pack(pady=5)
        tk.Label(self.root, text="Confirm Password:", bg="#FFFFFF").pack(pady=(10, 0))
        self.pw2_entry = tk.Entry(self.root, show="*", width=30, font=("Helvetica", 12), justify="center")
        self.pw2_entry.pack(pady=5)

        def create_master():
            pw1, pw2 = self.pw1_entry.get(), self.pw2_entry.get()
            if not pw1 or not pw2:
                messagebox.showerror("Error", "Please fill in both fields.")
                return
            if pw1 != pw2:
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return
            
            try:
                setup_master_password(pw1)
                messagebox.showinfo("Success", "Master password set securely!\n\n⚠️ WARNING: If you forget this password, it cannot be recovered.")
                self.show_main_app()
            except Exception as e:
                messagebox.showerror("Setup Error", f"Could not create master password: {e}")

        self.pw1_entry.bind("<Return>", lambda e: create_master())
        self.pw2_entry.bind("<Return>", lambda e: create_master())

        ttk.Button(self.root, text="Set Master Password", style="Success.TButton", command=create_master).pack(pady=25, ipadx=20, ipady=5)

    def show_main_app(self):
        self.clear_screen()
        main_frame = tk.Frame(self.root, bg="#FFFFFF", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Bottom and Data frames packed first to stay at the bottom
        bottom_frame = tk.Frame(main_frame, bg="#FFFFFF")
        bottom_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        data_frame = tk.LabelFrame(main_frame, text=" 🔄 Data Transfer ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        data_frame.pack(fill="x", side="bottom", pady=10)
        btn_frame = tk.Frame(data_frame, bg="#FFFFFF")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="📤 Export", style="Success.TButton", command=lambda: show_export_dialog(self.root)).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="📥 Import", style="Primary.TButton", command=lambda: show_import_dialog(self.root, self.after_import_callback)).pack(side="left", padx=10)

        # Header
        header_frame = tk.Frame(main_frame, bg="#FFFFFF")
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text="🔐 iBijan Pass", font=("Helvetica", 16, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(side="left")
        ttk.Button(header_frame, text="💡 About", style="Primary.TButton", command=lambda: show_about_dialog(self.root)).pack(side="right", padx=5)
        ttk.Button(header_frame, text="📚 Help Guide", style="Primary.TButton", command=lambda: show_comprehensive_help(self.root)).pack(side="right")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        self.tab_mental = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_mental, text=" 🧠 Mental Mode ")
        self.build_mental_mode_ui(self.tab_mental)

        self.tab_crypto = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_crypto, text=" 🔐 Cryptographic Mode ")
        self.build_crypto_mode_ui(self.tab_crypto)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Bottom Buttons
        ttk.Button(bottom_frame, text="📁 Open Config", style="Primary.TButton", command=lambda: open_config_folder(self.root)).pack(side="left", padx=2)
        ttk.Button(bottom_frame, text="📍 File Locations", style="Primary.TButton", command=lambda: show_file_locations(self.root)).pack(side="left", padx=2)
        
        def _clear_vault_action():
            if messagebox.askyesno("Confirm", "Permanently delete ALL saved passwords?", parent=self.root):
                success, msg = clear_vault()
                messagebox.showinfo("Vault", msg, parent=self.root)

        ttk.Button(bottom_frame, text="⚠️ Clear Vault", style="Danger.TButton", command=_clear_vault_action).pack(side="right", padx=(2, 10))
        ttk.Button(bottom_frame, text="🔥 Factory Reset", style="Danger.TButton", command=lambda: factory_reset(self.root, self.root.destroy)).pack(side="right", padx=2)

    def on_tab_change(self, event):
        """Clear the Master Secret if the user switches tabs to prevent accidental leaks."""
        if hasattr(self, 'crypto_master_secret_entry'):
            self.crypto_master_secret_entry.delete(0, tk.END)

    # ==========================================
    # MENTAL MODE UI
    # ==========================================
    def build_mental_mode_ui(self, parent):
        profile_frame = tk.LabelFrame(parent, text=" 📁 Saved Patterns ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        profile_frame.pack(fill="x", pady=(10, 5))

        tk.Label(profile_frame, text="Select Pattern:", bg="#FFFFFF").grid(row=0, column=0, padx=5, pady=10)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var, width=30, state="readonly")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=10)
        self.update_profile_combo()
        
        btn_load = ttk.Button(profile_frame, text="📥 Load Pattern", style="Primary.TButton", command=self.load_selected_profile)
        btn_load.grid(row=0, column=2, padx=2)
        ToolTip(btn_load, "Load the selected pattern to quickly generate a new password.")

        ttk.Button(profile_frame, text="🗑️ Delete Pattern", style="Danger.TButton", command=self.delete_selected_profile).grid(row=0, column=3, padx=2)

        hint_label = tk.Label(parent, text="Hint: Save your base components as a Pattern. Load it, then just change the Service Name for each new service.", font=("Helvetica", 9), fg=COLOR_NEUTRAL, bg="#FFFFFF")
        hint_label.pack(fill="x", pady=(0, 10))

        settings_frame = tk.LabelFrame(parent, text=" 🔧 Password Settings ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        settings_frame.pack(fill="x", pady=(0, 15))
        
        vcmd_pref = (self.root.register(validate_prefix), '%P')
        vcmd_base = (self.root.register(validate_base_number), '%P')
        vcmd_spec = (self.root.register(validate_special_chars), '%P')
        vcmd_svc = (self.root.register(validate_service_name), '%P')
        vcmd_cap = (self.root.register(validate_capitalize_letter), '%P')

        tk.Label(settings_frame, text="Pattern Name:", bg="#FFFFFF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.profile_name_entry = PlaceholderEntry(settings_frame, placeholder="e.g., MyBasePattern", width=25)
        self.profile_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(settings_frame, text="💾 Save Pattern", style="Success.TButton", command=self.save_current_profile).grid(row=0, column=2, padx=10)

        self.require_master_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_frame, text="🔒 Require Master Password to load this pattern", variable=self.require_master_var, bg="#FFFFFF").grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        tk.Label(settings_frame, text="Prefix:", bg="#FFFFFF").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.prefix_entry = PlaceholderEntry(settings_frame, placeholder="e.g., London", width=25, validate="key", validatecommand=vcmd_pref)
        self.prefix_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Base Number:", bg="#FFFFFF").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.base_entry = PlaceholderEntry(settings_frame, placeholder="e.g., 100", width=25, validate="key", validatecommand=vcmd_base)
        self.base_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Special Characters:", bg="#FFFFFF").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.special_entry = PlaceholderEntry(settings_frame, placeholder="e.g., @#!", width=25, validate="key", validatecommand=vcmd_spec)
        self.special_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Service Name:", bg="#FFFFFF").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.service_entry = PlaceholderEntry(settings_frame, placeholder="e.g., google", width=25, validate="key", validatecommand=vcmd_svc)
        self.service_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.service_entry.bind("<Return>", lambda e: self.generate_password())

        tk.Label(settings_frame, text="Capitalize Letter(s):", bg="#FFFFFF").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.capitalize_entry = PlaceholderEntry(settings_frame, placeholder="e.g., G or GM", width=25, validate="key", validatecommand=vcmd_cap)
        self.capitalize_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Pattern:", bg="#FFFFFF").grid(row=7, column=0, sticky="w", padx=5, pady=10)
        self.pattern_var = tk.StringVar(value=DEFAULT_PATTERN)
        ttk.Combobox(settings_frame, textvariable=self.pattern_var, values=list(PASSWORD_PATTERNS.keys()), width=40, state="readonly").grid(row=7, column=1, columnspan=2, sticky="w", padx=5)

        tk.Label(settings_frame, text="Note (Optional):", bg="#FFFFFF").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.note_entry = PlaceholderEntry(settings_frame, placeholder="e.g., Work Email Account", width=40)
        self.note_entry.grid(row=8, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        action_frame = tk.Frame(parent, bg="#FFFFFF")
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="🔐 Generate", style="Primary.TButton", command=self.generate_password).pack(side="left", padx=(0, 5), ipadx=5, ipady=5)
        ttk.Button(action_frame, text="💾 Save to Vault", style="Success.TButton", command=self.save_to_vault).pack(side="left", padx=5)
        ttk.Button(action_frame, text="📋 View Vault", style="Primary.TButton", command=self.view_vault).pack(side="left", padx=5)
        ttk.Button(action_frame, text="👁️ Preview All", style="Primary.TButton", command=self.show_preview_all_dialog).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🧹 Clear All", style="Neutral.TButton", command=self.clear_inputs).pack(side="left", padx=5)
                # --- NEW: Security Tip Panel ---
        tip_frame = tk.Frame(parent, bg="#E8ECFA", bd=1, relief="solid")
        tip_frame.pack(fill="both", expand=True, pady=(15, 10), padx=10)
        
        tk.Label(tip_frame, text="💡 Security Tip", font=("Helvetica", 11, "bold"), fg=BRAND_PRIMARY, bg="#E8ECFA").pack(anchor="w", padx=15, pady=(15, 5))
        tk.Label(tip_frame, text="Mental Mode relies on your personal pattern. Never share your formula or reuse the exact same prefix for high-security accounts (like banking) and casual accounts.", font=("Helvetica", 10), fg="#333333", bg="#E8ECFA", wraplength=600, justify="left").pack(anchor="w", padx=15, pady=(0, 15))

    # ==========================================
    # CRYPTOGRAPHIC MODE UI
    # ==========================================
    def build_crypto_mode_ui(self, parent):
        top_frame = tk.Frame(parent, bg="#FFFFFF")
        top_frame.pack(fill="x", pady=(10, 5))
        
        tk.Label(top_frame, text="Cryptographic Mode generates site-specific passwords from a Master Secret without saving them.", font=("Helvetica", 9), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(anchor="w", padx=5)

        # Saved Services Frame
        service_frame = tk.LabelFrame(parent, text=" 🔐 Saved Services ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        service_frame.pack(fill="x", pady=(5, 10))

        tk.Label(service_frame, text="Load Service:", bg="#FFFFFF").grid(row=0, column=0, padx=5, pady=10)
        self.crypto_service_var = tk.StringVar()
        self.crypto_service_combo = ttk.Combobox(service_frame, textvariable=self.crypto_service_var, width=30, state="readonly")
        self.crypto_service_combo.grid(row=0, column=1, padx=5, pady=10)
        self.update_crypto_combo()
        
        ttk.Button(service_frame, text="📥 Load", style="Primary.TButton", command=self.load_crypto_service).grid(row=0, column=2, padx=2)
        ttk.Button(service_frame, text="🗑️ Delete", style="Danger.TButton", command=self.delete_crypto_service).grid(row=0, column=3, padx=2)

        # Settings Frame
        settings_frame = tk.LabelFrame(parent, text=" ⚙️ Generation Settings ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        settings_frame.pack(fill="x", pady=(0, 15))

        # Master Secret (Masked)
        tk.Label(settings_frame, text="Master Secret:", bg="#FFFFFF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.crypto_master_secret_entry = tk.Entry(settings_frame, width=30, show="*")
        self.crypto_master_secret_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Service Name:", bg="#FFFFFF").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.crypto_svc_entry = PlaceholderEntry(settings_frame, placeholder="e.g., google", width=30)
        self.crypto_svc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Account/Username:", bg="#FFFFFF").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.crypto_acct_entry = PlaceholderEntry(settings_frame, placeholder="e.g., user@email.com", width=30)
        self.crypto_acct_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(settings_frame, text="Password Length:", bg="#FFFFFF").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.crypto_length_var = tk.IntVar(value=16)
        tk.Spinbox(settings_frame, from_=4, to=128, textvariable=self.crypto_length_var, width=5).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Checkboxes for policies
        self.crypto_upper_var = tk.BooleanVar(value=True)
        self.crypto_lower_var = tk.BooleanVar(value=True)
        self.crypto_digits_var = tk.BooleanVar(value=True)
        self.crypto_symbols_var = tk.BooleanVar(value=True)

        policy_frame = tk.Frame(settings_frame, bg="#FFFFFF")
        policy_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        tk.Checkbutton(policy_frame, text="Uppercase", variable=self.crypto_upper_var, bg="#FFFFFF").pack(side="left", padx=5)
        tk.Checkbutton(policy_frame, text="Lowercase", variable=self.crypto_lower_var, bg="#FFFFFF").pack(side="left", padx=5)
        tk.Checkbutton(policy_frame, text="Digits", variable=self.crypto_digits_var, bg="#FFFFFF").pack(side="left", padx=5)
        tk.Checkbutton(policy_frame, text="Symbols", variable=self.crypto_symbols_var, bg="#FFFFFF").pack(side="left", padx=5)

        # Actions
        action_frame = tk.Frame(parent, bg="#FFFFFF")
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="🔐 Generate", style="Primary.TButton", command=self.generate_crypto_password_action).pack(side="left", padx=(0, 10), ipadx=10, ipady=5)
        ttk.Button(action_frame, text="💾 Save Service", style="Success.TButton", command=self.save_crypto_service_action).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🧹 Clear", style="Neutral.TButton", command=self.clear_crypto_inputs).pack(side="left", padx=5)
                # --- NEW: Security Tip Panel ---
        tip_frame = tk.Frame(parent, bg="#E8ECFA", bd=1, relief="solid")
        tip_frame.pack(fill="both", expand=True, pady=(15, 10), padx=10)
        
        tk.Label(tip_frame, text="🛡️ Security Note", font=("Helvetica", 11, "bold"), fg=BRAND_PRIMARY, bg="#E8ECFA").pack(anchor="w", padx=15, pady=(15, 5))
        tk.Label(tip_frame, text="Your Master Secret is mathematically used to generate these passwords. It is NEVER saved to disk. If you forget it, you will permanently lose access to all passwords in this mode.", font=("Helvetica", 10), fg="#333333", bg="#E8ECFA", wraplength=600, justify="left").pack(anchor="w", padx=15, pady=(0, 15))
        
    def update_crypto_combo(self):
        try:
            services = crypto_data_manager.get_services()
            display_names = []
            self._crypto_key_map = {} # Map display names to actual SHA256 keys
            
            for key, data in services.items():
                svc = data.get("service_name", "")
                acct = data.get("account", "")
                display_str = f"{svc} | {acct}" if acct else svc
                display_names.append(display_str)
                self._crypto_key_map[display_str] = key
            
            self.crypto_service_combo['values'] = display_names
            if display_names:
                self.crypto_service_combo.current(0)
        except Exception as e:
            messagebox.showerror("Data Error", f"Could not load crypto services:\n{e}", parent=self.root)
            
    def load_crypto_service(self):
        display_str = self.crypto_service_var.get()
        if not display_str:
            messagebox.showwarning("Select", "Please select a service to load.", parent=self.root)
            return
            
        key = getattr(self, '_crypto_key_map', {}).get(display_str)
        if not key:
            return
            
        data = load_crypto_service(key)
        if data:
            self.crypto_svc_entry._clear_placeholder()
            self.crypto_svc_entry.delete(0, tk.END)
            self.crypto_svc_entry.insert(0, data.get("service_name", ""))
            
            self.crypto_acct_entry._clear_placeholder()
            self.crypto_acct_entry.delete(0, tk.END)
            self.crypto_acct_entry.insert(0, data.get("account", ""))
            
            self.crypto_length_var.set(data.get("length", 16))
            self.crypto_upper_var.set(data.get("use_upper", True))
            self.crypto_lower_var.set(data.get("use_lower", True))
            self.crypto_digits_var.set(data.get("use_digits", True))
            self.crypto_symbols_var.set(data.get("use_symbols", True))
            
            self.crypto_master_secret_entry.delete(0, tk.END)
            self.crypto_master_secret_entry.focus()

    def delete_crypto_service(self):
        display_str = self.crypto_service_var.get()
        if not display_str: return
        
        key = getattr(self, '_crypto_key_map', {}).get(display_str)
        if not key: return
        
        if messagebox.askyesno("Confirm", f"Delete service entry '{display_str}'?", parent=self.root):
            if delete_crypto_service(key):
                self.update_crypto_combo()
                self.crypto_service_var.set("")
                
    def generate_crypto_password_action(self):
        secret = self.crypto_master_secret_entry.get()
        svc = self.crypto_svc_entry.get_value().strip()
        acct = self.crypto_acct_entry.get_value().strip()
        
        if not secret or not svc:
            messagebox.showerror("Error", "Master Secret and Service Name are required.", parent=self.root)
            return
            
        from .crypto_storage import _get_key
        key = _get_key(svc, acct)
        
        # Check if we have a saved salt for this service
        saved_data = load_crypto_service(key)
        if saved_data and saved_data.get("salt"):
            salt = decode_salt(saved_data["salt"])
        else:
            # Generate a new salt if this is a brand new service
            salt = generate_salt()
            salt_b64 = encode_salt(salt)
            
            # FIXED: Updated arguments to match new crypto_storage signature
            save_crypto_service(
                service_name=svc,
                account=acct,
                algorithm_version="1.0",
                password_revision=1,
                length=self.crypto_length_var.get(),
                use_upper=self.crypto_upper_var.get(),
                use_lower=self.crypto_lower_var.get(),
                use_digits=self.crypto_digits_var.get(),
                use_symbols=self.crypto_symbols_var.get(),
                salt_b64=salt_b64
            )
            self.update_crypto_combo()

        try:
            # FIXED: Changed 'version=1' to 'password_revision=1'
            pw = generate_crypto_password(
                master_secret=secret,
                salt=salt,
                service=svc,
                account=acct,
                password_revision=1,
                length=self.crypto_length_var.get(),
                use_upper=self.crypto_upper_var.get(),
                use_lower=self.crypto_lower_var.get(),
                use_digits=self.crypto_digits_var.get(),
                use_symbols=self.crypto_symbols_var.get()
            )
            
            clipboard_manager.copy_to_clipboard(pw)
            messagebox.showinfo("Generated", f"Cryptographic password for '{svc}' generated and copied to clipboard.\n\n(This password is deterministic and will be the same every time).", parent=self.root)
            
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)
    def save_crypto_service_action(self):
        svc = self.crypto_svc_entry.get_value().strip()
        acct = self.crypto_acct_entry.get_value().strip()
        
        if not svc:
            messagebox.showerror("Error", "Service Name is required.", parent=self.root)
            return
            
        from .crypto_storage import _get_key
        key = _get_key(svc, acct)
        
        # Check if it already exists
        saved_data = load_crypto_service(key)
        if saved_data:
            salt_b64 = saved_data["salt"]
        else:
            salt_b64 = encode_salt(generate_salt())
            
        # FIXED: Updated arguments to match new crypto_storage signature
        success, msg = save_crypto_service(
            service_name=svc,
            account=acct,
            algorithm_version="1.0",
            password_revision=1,
            length=self.crypto_length_var.get(),
            use_upper=self.crypto_upper_var.get(),
            use_lower=self.crypto_lower_var.get(),
            use_digits=self.crypto_digits_var.get(),
            use_symbols=self.crypto_symbols_var.get(),
            salt_b64=salt_b64
        )
        
        if success:
            messagebox.showinfo("Saved", msg, parent=self.root)
            self.update_crypto_combo()
        else:
            messagebox.showerror("Error", msg, parent=self.root)
                        
    def clear_crypto_inputs(self):
        self.crypto_master_secret_entry.delete(0, tk.END)
        self.crypto_svc_entry._clear_placeholder()
        self.crypto_svc_entry.delete(0, tk.END)
        self.crypto_svc_entry._add_placeholder()
        self.crypto_acct_entry._clear_placeholder()
        self.crypto_acct_entry.delete(0, tk.END)
        self.crypto_acct_entry._add_placeholder()
        self.crypto_length_var.set(16)
        self.crypto_upper_var.set(True)
        self.crypto_lower_var.set(True)
        self.crypto_digits_var.set(True)
        self.crypto_symbols_var.set(True)

    # ==========================================
    # MENTAL MODE LOGIC (Unchanged)
    # ==========================================
    def update_profile_combo(self):
        try:
            profiles = data_manager.get_profiles()
            display_names = [f"🔒 {name}" if data.get("require_master") else f"📁 {name}" for name, data in profiles.items()]
            self.profile_combo['values'] = display_names
            if display_names:
                self.profile_combo.current(0)
        except Exception as e:
            messagebox.showerror("Data Error", f"Could not load patterns:\n{e}\n\nSaving is disabled to prevent data loss.", parent=self.root)
            self.profile_combo['values'] = ["⚠️ ERROR: Corrupted"]

    def after_import_callback(self):
        self.update_profile_combo()
        self.update_crypto_combo()
        if self.profile_var.get():
            self.load_selected_profile(show_msg=False)
            
    def load_selected_profile(self, show_msg=True):
        display_name = self.profile_var.get()
        profiles = data_manager.get_profiles()
        
        if not display_name:
            if not profiles:
                messagebox.showinfo("No Patterns", "You haven't saved any patterns yet.\n\nPlease fill out the settings and click 'Save Pattern' first.", parent=self.root)
            else:
                messagebox.showwarning("Select a Pattern", "Please select a pattern from the dropdown menu first, then click Load.", parent=self.root)
            return
            
        profile_name = display_name.replace("🔒 ", "").replace("📁 ", "")
        profile_data = load_profile(profile_name)
        
        if profile_data:
            if profile_data.get("require_master") and not verify_master_password_for_profile(self.root):
                return
            
            for entry, key in [(self.prefix_entry, "prefix"), (self.base_entry, "base_number"), 
                               (self.special_entry, "special_chars"), (self.capitalize_entry, "capitalize_letter")]:
                entry._clear_placeholder()
                entry.delete(0, tk.END)
                entry.insert(0, profile_data.get(key, ""))
                if not entry.get(): entry._add_placeholder()

            self.pattern_var.set(profile_data.get("password_pattern", DEFAULT_PATTERN))
            
            if show_msg:
                messagebox.showinfo("Loaded", f"Pattern '{profile_name}' loaded. You can now change the Service Name.", parent=self.root)
                
    def save_current_profile(self):
        name = self.profile_name_entry.get_value().strip() or f"Pattern_{len(data_manager.get_profiles()) + 1}"
        success, msg = save_profile(
            name, self.prefix_entry.get_value(), self.base_entry.get_value(), self.special_entry.get_value(),
            self.capitalize_entry.get_value(), self.pattern_var.get(),
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
        if messagebox.askyesno("Confirm", f"Delete pattern '{name}'?", parent=self.root):
            if delete_profile(name):
                self.update_profile_combo()
                self.profile_var.set("")

    def generate_password(self):
        pw, warning = build_password(
            self.prefix_entry.get_value(), self.base_entry.get_value(), self.special_entry.get_value(),
            self.service_entry.get_value(), self.capitalize_entry.get_value(),
            self.pattern_var.get()
        )
        
        if warning: messagebox.showwarning("Warning", warning, parent=self.root)
            
        if pw:
            if clipboard_manager.copy_to_clipboard(pw):
                messagebox.showinfo("Generated", f"Password copied to clipboard:\n{pw}", parent=self.root)
            else:
                messagebox.showinfo("Generated", f"Password (copy manually):\n{pw}", parent=self.root)
            self.last_generated_password = pw

    def save_to_vault(self):
        svc = self.service_entry.get_value()
        if not svc:
            messagebox.showerror("Error", "Please enter a Service Name first!", parent=self.root)
            return

        pw, warning = build_password(
            self.prefix_entry.get_value(), self.base_entry.get_value(), self.special_entry.get_value(),
            svc, self.capitalize_entry.get_value(),
            self.pattern_var.get()
        )

        if not pw:
            messagebox.showerror("Error", warning or "Please fill in all fields to generate a password.", parent=self.root)
            return
            
        note = self.note_entry.get_value()

        success, msg = save_to_vault(svc, pw, note)
        if success:
            messagebox.showinfo("Success", f"{msg}\nPassword: {pw}", parent=self.root)
        else:
            messagebox.showerror("Error", msg, parent=self.root)

    def show_preview_all_dialog(self):
        prefix = self.prefix_entry.get_value()
        base_number = self.base_entry.get_value()
        special_chars = self.special_entry.get_value()
        service_name = self.service_entry.get_value()
        user_letter = self.capitalize_entry.get_value()

        if not all([prefix, base_number, special_chars, service_name]):
            messagebox.showerror("Error", "Please fill in all required fields (Prefix, Base, Special, Service) to preview patterns.", parent=self.root)
            return

        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview All Patterns")
        preview_window.geometry("950x480") 
        preview_window.transient(self.root)
        preview_window.grab_set()
        preview_window.resizable(False, False)

        bottom_btn_frame = tk.Frame(preview_window)
        bottom_btn_frame.pack(side="bottom", fill="x", pady=15)
        ttk.Button(bottom_btn_frame, text="Close", style="Danger.TButton", command=preview_window.destroy).pack()

        tk.Label(preview_window, text="👁️ Preview All Password Patterns", font=("Helvetica", 14, "bold"), fg=BRAND_PRIMARY).pack(pady=(10, 5))
        tk.Label(preview_window, text="Pick your favorite pattern, copy it, or give it a name to save.", font=("Helvetica", 9), fg=COLOR_NEUTRAL).pack(pady=(0, 10))

        header_frame = tk.Frame(preview_window)
        header_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(header_frame, text="Pattern Layout", font=("Helvetica", 10, "bold"), width=38, anchor="w").pack(side="left")
        tk.Label(header_frame, text="Generated Password", font=("Helvetica", 10, "bold"), width=22, anchor="w").pack(side="left")
        tk.Label(header_frame, text="Pattern Name", font=("Helvetica", 10, "bold"), width=18, anchor="w").pack(side="left")
        tk.Label(header_frame, text="Actions", font=("Helvetica", 10, "bold"), width=15, anchor="w").pack(side="left")

        ttk.Separator(preview_window, orient='horizontal').pack(fill='x', padx=20, pady=5)

        list_frame = tk.Frame(preview_window, bg="#FFFFFF")
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        def copy_specific_pw(pw):
            if clipboard_manager.copy_to_clipboard(pw):
                messagebox.showinfo("Copied", "Password copied to clipboard!", parent=preview_window)

        def save_specific_pattern(pattern_key, entry_widget):
            name = entry_widget.get_value().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a name for this pattern.", parent=preview_window)
                return
            
            if name in data_manager.get_profiles():
                messagebox.showerror("Error", f"A pattern named '{name}' already exists. Please choose another name.", parent=preview_window)
                return

            success, msg = save_profile(
                name, prefix, base_number, special_chars, 
                user_letter, pattern_key, False 
            )
            
            if success:
                messagebox.showinfo("Saved", f"Pattern '{name}' saved successfully!", parent=preview_window)
                entry_widget._clear_placeholder()
                entry_widget.delete(0, tk.END)
                entry_widget._add_placeholder()
                self.update_profile_combo()
            else:
                messagebox.showerror("Error", msg, parent=preview_window)

        for pattern_key in PASSWORD_PATTERNS.keys():
            pw, warning = build_password(prefix, base_number, special_chars, service_name, user_letter, pattern_key)
            
            row_frame = tk.Frame(list_frame, bg="#FFFFFF")
            row_frame.pack(fill="x", pady=5)

            tk.Label(row_frame, text=pattern_key, width=38, anchor="w", bg="#FFFFFF", font=("Helvetica", 9)).pack(side="left")
            tk.Label(row_frame, text=pw, width=22, anchor="w", bg="#FFFFFF", font=("Helvetica", 10, "bold"), fg=COLOR_SUCCESS).pack(side="left")
            
            name_entry = PlaceholderEntry(row_frame, placeholder="e.g., MyPattern", width=18)
            name_entry.pack(side="left", padx=5)
            
            action_frame = tk.Frame(row_frame, bg="#FFFFFF")
            action_frame.pack(side="left", padx=5)

            ttk.Button(
                action_frame, text="📋 Copy", style="Primary.TButton", 
                command=lambda p=pw: copy_specific_pw(p)
            ).pack(side="left", padx=(0, 5))

            ttk.Button(
                action_frame, text="💾 Save", style="Success.TButton", 
                command=lambda k=pattern_key, e=name_entry: save_specific_pattern(k, e)
            ).pack(side="left")

    def clear_inputs(self):
        for entry in [self.profile_name_entry, self.prefix_entry, self.base_entry, 
                      self.special_entry, self.service_entry, self.capitalize_entry, self.note_entry]:
            entry._clear_placeholder()
            entry.delete(0, tk.END)
            entry._add_placeholder()
        
        self.pattern_var.set(DEFAULT_PATTERN)
        self.last_generated_password = ""

    def view_vault(self):
        vault_data = get_vault_data()
        if not vault_data:
            messagebox.showinfo("Vault Empty", "No saved passwords.", parent=self.root)
            return
        
        vw = tk.Toplevel(self.root)
        vw.title("Saved Passwords")
        vw.geometry("600x400")
        vw.minsize(550, 350)
        
        tree_frame = tk.Frame(vw)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        tree = ttk.Treeview(tree_frame, columns=("Service", "Password", "Note"), show="headings", selectmode="extended", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)
        
        tree.heading("Service", text="Service")
        tree.heading("Password", text="Password")
        tree.heading("Note", text="Note")
        
        tree.column("Service", width=120)
        tree.column("Password", width=150)
        tree.column("Note", width=250)

        def refresh_tree():
            for item in tree.get_children():
                tree.delete(item)
            new_data = get_vault_data()
            if new_data:
                for row in new_data:
                    tree.insert("", "end", values=row)

        for row in vault_data:
            tree.insert("", "end", values=row)
            
        tree.pack(fill="both", expand=True)

        def select_all(event=None):
            tree.selection_set(tree.get_children())
            return "break"
        
        tree.bind("<Control-a>", select_all)
        tree.bind("<Control-A>", select_all)

        def copy_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Copy", "Please select a row first.", parent=vw)
                return
            item = tree.item(selected[0])
            password = item['values'][1]
            clipboard_manager.copy_to_clipboard(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!", parent=vw)

        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Delete", "Please select at least one row to delete.", parent=vw)
                return
            
            if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} password(s)?\nThis action cannot be undone.", parent=vw):
                return
                
            entries_to_delete = []
            for item_id in selected:
                item = tree.item(item_id)
                vals = item['values']
                if len(vals) >= 2:
                    entries_to_delete.append((vals[0], vals[1]))

            success, msg = delete_from_vault(entries_to_delete)
            if success:
                messagebox.showinfo("Success", msg, parent=vw)
                refresh_tree()
                if not tree.get_children():
                    vw.destroy()
            else:
                messagebox.showerror("Error", msg, parent=vw)

        btn_frame = tk.Frame(vw)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="📋 Copy Selected", style="Primary.TButton", command=copy_selected).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🗑️ Delete Selected", style="Danger.TButton", command=delete_selected).pack(side="left", padx=10)