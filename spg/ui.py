import tkinter as tk
from tkinter import messagebox, ttk
import os

from .clipboard import clipboard_manager, ToolTip
from .config import (
    APP_VERSION, APP_WEBSITE, CONFIG_DIR, PASSWORD_PATTERNS, DEFAULT_PATTERN,
    BRAND_PRIMARY, BRAND_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_NEUTRAL
)
from .crypto import is_master_set, save_master_hash, hash_password, verify_master
from .validators import (
    validate_prefix, validate_base_number, validate_special_chars,
    validate_service_name, validate_capitalize_letter, validate_profile_name
)
from .storage import (
    data_manager, save_profile, delete_profile, load_profile,
    save_to_vault, get_vault_data, clear_vault
)
from .generator import build_password
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
        self.root.title(f"iBijan Pass v{APP_VERSION} - Smart Password Generator")
        self.root.minsize(650, 850)
        self.root.configure(bg="#FFFFFF")
        
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            try:
                icon_img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon_img)
            except Exception:
                pass
        
        self.last_generated_password = ""
        self._setup_styles()
        
        self.root.bind_class("Entry", "<Control-a>", self._select_all)
        self.root.bind_class("Entry", "<Control-A>", self._select_all)
        self.root.bind_class("TEntry", "<Control-a>", self._select_all)
        self.root.bind_class("TEntry", "<Control-A>", self._select_all)

        self.check_authentication()

    def _select_all(self, event):
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')
        return 'break'

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Primary Button (Blue)
        style.configure("Primary.TButton", background=BRAND_PRIMARY, foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Primary.TButton", background=[("active", BRAND_DARK)])
        
        # Success Button (Green)
        style.configure("Success.TButton", background=COLOR_SUCCESS, foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Success.TButton", background=[("active", "#008a7b")])
        
        # Danger Button (Red)
        style.configure("Danger.TButton", background=COLOR_DANGER, foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Danger.TButton", background=[("active", "#a32929")])

        # NEW: Neutral Button (Grey-Blue) for Clear
        style.configure("Neutral.TButton", background="#6B7280", foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Neutral.TButton", background=[("active", "#4B5563")])

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def check_authentication(self):
        self.clear_screen()
        if is_master_set():
            self.show_login_screen()
        else:
            self.show_setup_screen()

    def show_login_screen(self):
        tk.Label(self.root, text="🔐 iBijan Pass", font=("Helvetica", 24, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(pady=(80, 5))
        tk.Label(self.root, text="Smart Password Generator", font=("Helvetica", 12), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(pady=(0, 40))
        tk.Label(self.root, text="Enter your master password", font=("Helvetica", 11), bg="#FFFFFF").pack(pady=10)
        
        self.login_entry = tk.Entry(self.root, show="*", width=28, font=("Helvetica", 14), justify="center")
        self.login_entry.pack(pady=10, ipady=5)
        self.login_entry.focus()
        
        ttk.Button(self.root, text="🔓 Unlock", style="Primary.TButton", command=self.authenticate).pack(pady=20, ipadx=30, ipady=5)
        self.login_entry.bind("<Return>", lambda e: self.authenticate())
        tk.Label(self.root, text=f"v{APP_VERSION} • {APP_WEBSITE}", font=("Helvetica", 8), fg=COLOR_NEUTRAL, bg="#FFFFFF").pack(side="bottom", pady=15)

    def authenticate(self):
        if verify_master(self.login_entry.get()):
            self.show_main_app()
        else:
            messagebox.showerror("Access Denied", "Incorrect master password.")
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
            save_master_hash(hash_password(pw1))
            messagebox.showinfo("Success", "Master password set!\n\n⚠️ WARNING: If you forget this password, it cannot be recovered.")
            self.show_main_app()

        self.pw1_entry.bind("<Return>", lambda e: create_master())
        self.pw2_entry.bind("<Return>", lambda e: create_master())

        ttk.Button(self.root, text="Set Master Password", style="Success.TButton", command=create_master).pack(pady=25, ipadx=20, ipady=5)

    def show_main_app(self):
        self.clear_screen()
        main_frame = tk.Frame(self.root, bg="#FFFFFF", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        header_frame = tk.Frame(main_frame, bg="#FFFFFF")
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text="🔐 iBijan Pass", font=("Helvetica", 16, "bold"), fg=BRAND_PRIMARY, bg="#FFFFFF").pack(side="left")
        ttk.Button(header_frame, text="💡 About", style="Primary.TButton", command=lambda: show_about_dialog(self.root)).pack(side="right", padx=5)
        ttk.Button(header_frame, text="📚 Help Guide", style="Primary.TButton", command=lambda: show_comprehensive_help(self.root)).pack(side="right")

        profile_frame = tk.LabelFrame(main_frame, text=" 📁 Password Profiles ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        profile_frame.pack(fill="x", pady=(0, 15))

        tk.Label(profile_frame, text="Select:", bg="#FFFFFF").grid(row=0, column=0, padx=5, pady=10)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var, width=30, state="readonly")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=10)
        self.update_profile_combo()
        
        # FIXED: No duplicated buttons here anymore
        btn_load = ttk.Button(profile_frame, text="📥 Load", style="Primary.TButton", command=self.load_selected_profile)
        btn_load.grid(row=0, column=2, padx=2)
        ToolTip(btn_load, "Load the selected profile from the dropdown menu.")

        ttk.Button(profile_frame, text="🗑️ Delete", style="Danger.TButton", command=self.delete_selected_profile).grid(row=0, column=3, padx=2)

        settings_frame = tk.LabelFrame(main_frame, text=" 🔧 Password Settings ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        settings_frame.pack(fill="x", pady=(0, 15))
        
        vcmd_pref = (self.root.register(validate_prefix), '%P')
        vcmd_base = (self.root.register(validate_base_number), '%P')
        vcmd_spec = (self.root.register(validate_special_chars), '%P')
        vcmd_svc = (self.root.register(validate_service_name), '%P')
        vcmd_cap = (self.root.register(validate_capitalize_letter), '%P')

        tk.Label(settings_frame, text="New Profile Name:", bg="#FFFFFF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.profile_name_entry = PlaceholderEntry(settings_frame, placeholder="e.g., MyBank", width=25)
        self.profile_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(settings_frame, text="💾 Save As New", style="Success.TButton", command=self.save_current_profile).grid(row=0, column=2, padx=10)

        self.require_master_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_frame, text="🔒 Require Master Password to load this profile", variable=self.require_master_var, bg="#FFFFFF").grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=5)

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

        tk.Label(settings_frame, text="Capitalize Letter:", bg="#FFFFFF").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.capitalize_entry = PlaceholderEntry(settings_frame, placeholder="e.g., G", width=25, validate="key", validatecommand=vcmd_cap)
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

        tk.Label(settings_frame, text="Note (Optional):", bg="#FFFFFF").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.note_entry = PlaceholderEntry(settings_frame, placeholder="e.g., Work Email Account", width=40)
        self.note_entry.grid(row=9, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        action_frame = tk.Frame(main_frame, bg="#FFFFFF")
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="🔐 Generate", style="Primary.TButton", command=self.generate_password).pack(side="left", padx=(0, 10), ipadx=10, ipady=5)
        ttk.Button(action_frame, text="💾 Save to Vault", style="Success.TButton", command=self.save_to_vault).pack(side="left", padx=5)
        ttk.Button(action_frame, text="📋 View Vault", style="Primary.TButton", command=self.view_vault).pack(side="left", padx=5)
        # Apply the Neutral style to the Clear button
        ttk.Button(action_frame, text="🧹 Clear", style="Neutral.TButton", command=self.clear_inputs).pack(side="left", padx=15)

        data_frame = tk.LabelFrame(main_frame, text=" 🔄 Data Transfer ", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg=BRAND_PRIMARY)
        data_frame.pack(fill="x", pady=10)
        btn_frame = tk.Frame(data_frame, bg="#FFFFFF")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="📤 Export", style="Success.TButton", command=lambda: show_export_dialog(self.root)).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="📥 Import", style="Primary.TButton", command=lambda: show_import_dialog(self.root, self.update_profile_combo)).pack(side="left", padx=10)

        bottom_frame = tk.Frame(main_frame, bg="#FFFFFF")
        bottom_frame.pack(fill="x", side="bottom", pady=10)
        
        ttk.Button(bottom_frame, text="📁 Open Config", style="Primary.TButton", command=lambda: open_config_folder(self.root)).pack(side="left", padx=2)
        ttk.Button(bottom_frame, text="📍 File Locations", style="Primary.TButton", command=lambda: show_file_locations(self.root)).pack(side="left", padx=2)
        
        def _clear_vault_action():
            if messagebox.askyesno("Confirm", "Permanently delete ALL saved passwords?", parent=self.root):
                success, msg = clear_vault()
                messagebox.showinfo("Vault", msg, parent=self.root)

        ttk.Button(bottom_frame, text="⚠️ Clear Vault", style="Danger.TButton", command=_clear_vault_action).pack(side="right", padx=(2, 10))
        ttk.Button(bottom_frame, text="🔥 Factory Reset", style="Danger.TButton", command=lambda: factory_reset(self.root, self.root.destroy)).pack(side="right", padx=2)

    def update_profile_combo(self):
        profiles = data_manager.get_profiles()
        display_names = [f"🔒 {name}" if data.get("require_master") else f"📁 {name}" for name, data in profiles.items()]
        self.profile_combo['values'] = display_names

    def load_selected_profile(self):
        display_name = self.profile_var.get()
        profiles = data_manager.get_profiles()
        
        if not display_name:
            if not profiles:
                messagebox.showinfo("No Profiles", 
                                    "You haven't saved any profiles yet.\n\n"
                                    "Please fill out the settings and click 'Save As New' first.", 
                                    parent=self.root)
            else:
                messagebox.showwarning("Select a Profile", 
                                       "Please select a profile from the dropdown menu first, then click Load.", 
                                       parent=self.root)
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

            self.quotation_var.set(profile_data.get("quotation_style", "single"))
            self.pattern_var.set(profile_data.get("password_pattern", DEFAULT_PATTERN))
            messagebox.showinfo("Loaded", f"Profile '{profile_name}' loaded.", parent=self.root)
            
    def save_current_profile(self):
        name = self.profile_name_entry.get_value().strip() or f"Profile_{len(data_manager.get_profiles()) + 1}"
        success, msg = save_profile(
            name, self.prefix_entry.get_value(), self.base_entry.get_value(), self.special_entry.get_value(),
            self.capitalize_entry.get_value(), self.quotation_var.get(), self.pattern_var.get(),
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
            self.prefix_entry.get_value(), self.base_entry.get_value(), self.special_entry.get_value(),
            self.service_entry.get_value(), self.capitalize_entry.get_value(),
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
        svc = self.service_entry.get_value()
        if not svc:
            messagebox.showerror("Error", "Please enter a Service Name first!", parent=self.root)
            return

        pw, warning = build_password(
            self.prefix_entry.get_value(), self.base_entry.get_value(), self.special_entry.get_value(),
            svc, self.capitalize_entry.get_value(),
            self.quotation_var.get(), self.pattern_var.get()
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

    def clear_inputs(self):
        for entry in [self.profile_name_entry, self.prefix_entry, self.base_entry, 
                      self.special_entry, self.service_entry, self.capitalize_entry, self.note_entry]:
            entry._clear_placeholder()
            entry.delete(0, tk.END)
            entry._add_placeholder()
        
        self.quotation_var.set("single")
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
        
        tree = ttk.Treeview(tree_frame, columns=("Service", "Password", "Note"), show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)
        
        tree.heading("Service", text="Service")
        tree.heading("Password", text="Password")
        tree.heading("Note", text="Note")
        
        tree.column("Service", width=120)
        tree.column("Password", width=150)
        tree.column("Note", width=250)
        
        for row in vault_data:
            tree.insert("", "end", values=row)
            
        tree.pack(fill="both", expand=True)

        def copy_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Copy", "Please select a row first.", parent=vw)
                return
            item = tree.item(selected[0])
            password = item['values'][1]
            clipboard_manager.copy_to_clipboard(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!", parent=vw)

        ttk.Button(vw, text="📋 Copy Selected Password", style="Primary.TButton", command=copy_selected).pack(pady=10)