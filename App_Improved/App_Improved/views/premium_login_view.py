import tkinter as tk
from tkinter import messagebox
import math
try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except ImportError:
    import tkinter.ttk as ttk
    HAS_CUSTOMTKINTER = False


class PremiumLoginView:
    """Premium modern login view with 2025 design trends"""
    
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login
        self.root.title("Duplicate Finder - Premium Login")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # Центрування вікна
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        if HAS_CUSTOMTKINTER:
            self._setup_premium_ui()
        else:
            self._setup_fallback_ui()

    def _setup_premium_ui(self):
        """Setup premium UI with 2025 design trends"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Gradient background using frames
        main_frame = ctk.CTkFrame(self.root, fg_color="#0a0e27")
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Animated gradient header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#0f1535", height=200)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Decorative circles (glassmorphism effect)
        circle1 = ctk.CTkFrame(header_frame, fg_color="#00d4ff", corner_radius=100, width=150, height=150)
        circle1.place(x=-50, y=-50)
        
        circle2 = ctk.CTkFrame(header_frame, fg_color="#ff006e", corner_radius=100, width=100, height=100)
        circle2.place(x=500, y=20)
        
        # Title with gradient effect
        title_label = ctk.CTkLabel(
            header_frame,
            text="✨ Duplicate Finder",
            font=("Helvetica", 48, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=40)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Advanced Document Analysis Platform",
            font=("Helvetica", 13),
            text_color="#a0d4ff"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Content frame with glassmorphism
        content_frame = ctk.CTkFrame(main_frame, fg_color="#0f1535", corner_radius=20)
        content_frame.pack(fill="both", expand=True, padx=30, pady=40)
        
        # Role selection with modern design
        role_label = ctk.CTkLabel(
            content_frame,
            text="Select Your Role",
            font=("Helvetica", 16, "bold"),
            text_color="#ffffff"
        )
        role_label.pack(pady=(20, 30))
        
        self.role_var = tk.StringVar(value="Гість")
        
        # Radio buttons with custom styling
        radio_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        radio_frame.pack(fill="x", pady=15)
        
        guest_radio = ctk.CTkRadioButton(
            radio_frame,
            text="👤 Guest User",
            variable=self.role_var,
            value="Гість",
            command=self.toggle_password,
            font=("Helvetica", 13),
            text_color="#ffffff",
            fg_color="#00d4ff",
            hover_color="#00a8cc"
        )
        guest_radio.pack(side="left", padx=15, pady=10)
        
        admin_radio = ctk.CTkRadioButton(
            radio_frame,
            text="👨‍💼 Administrator",
            variable=self.role_var,
            value="Адміністратор",
            command=self.toggle_password,
            font=("Helvetica", 13),
            text_color="#ffffff",
            fg_color="#ff006e",
            hover_color="#cc0055"
        )
        admin_radio.pack(side="left", padx=15, pady=10)
        
        # Password frame with smooth transitions
        self.password_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.password_frame.pack(fill="x", pady=20)
        
        password_label = ctk.CTkLabel(
            self.password_frame,
            text="🔐 Administrator Password",
            font=("Helvetica", 12, "bold"),
            text_color="#ffffff"
        )
        password_label.pack(pady=(0, 12))
        
        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="Enter your secure password",
            show="•",
            font=("Helvetica", 12),
            height=45,
            border_width=2,
            border_color="#ff006e",
            fg_color="#1a1f3a",
            text_color="#ffffff"
        )
        self.password_entry.pack(fill="x", padx=5)
        
        self.password_frame.pack_forget()
        
        # Login button with hover effects
        login_button = ctk.CTkButton(
            content_frame,
            text="🚀 Sign In",
            command=self.login,
            font=("Helvetica", 14, "bold"),
            height=50,
            corner_radius=12,
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#0a0e27",
            border_width=0
        )
        login_button.pack(fill="x", padx=5, pady=30)
        
        # Info section
        info_frame = ctk.CTkFrame(content_frame, fg_color="#1a1f3a", corner_radius=10)
        info_frame.pack(fill="x", padx=5, pady=10)
        
        info_text = ctk.CTkLabel(
            info_frame,
            text="💡 Demo Password: admin123",
            font=("Helvetica", 10),
            text_color="#a0d4ff"
        )
        info_text.pack(pady=10)
        
        # Footer
        footer_label = ctk.CTkLabel(
            main_frame,
            text="© 2025 Duplicate Finder • Powered by Advanced AI",
            font=("Helvetica", 9),
            text_color="#666666"
        )
        footer_label.pack(pady=10)

    def _setup_fallback_ui(self):
        """Fallback UI without customtkinter"""
        self.root.configure(bg="#0a0e27")
        
        ttk.Label(self.root, text="Duplicate Finder - Sign In", font=("Helvetica", 16, "bold"), 
                  background="#0a0e27", foreground="#00d4ff").pack(pady=20)

        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)

        ttk.Label(frame, text="Select Role", font=("Helvetica", 12)).grid(row=0, column=0, pady=10, columnspan=2)
        self.role_var = tk.StringVar(value="Гість")
        ttk.Radiobutton(frame, text="Guest", variable=self.role_var, value="Гість", 
                        command=self.toggle_password).grid(row=1, column=0, padx=10, pady=5)
        ttk.Radiobutton(frame, text="Administrator", variable=self.role_var, value="Адміністратор", 
                        command=self.toggle_password).grid(row=1, column=1, padx=10, pady=5)

        self.password_label = ttk.Label(frame, text="Password")
        self.password_entry = tk.Entry(frame, show="*", width=20)
        self.password_entry.grid(row=3, column=0, columnspan=2, pady=5)
        self.password_label.grid(row=2, column=0, columnspan=2, pady=5)
        self.toggle_password()

        ttk.Button(frame, text="Sign In", command=self.login).grid(row=4, column=0, columnspan=2, pady=20)

    def toggle_password(self):
        """Toggle password field visibility"""
        if self.role_var.get() == "Гість":
            if HAS_CUSTOMTKINTER:
                self.password_frame.pack_forget()
            else:
                self.password_label.grid_forget()
                self.password_entry.grid_forget()
        else:
            if HAS_CUSTOMTKINTER:
                self.password_frame.pack(fill="x", pady=20)
            else:
                self.password_label.grid(row=2, column=0, columnspan=2, pady=5)
                self.password_entry.grid(row=3, column=0, columnspan=2, pady=5)

    def login(self):
        """Handle login button click"""
        role = self.role_var.get()
        password = self.password_entry.get() if role == "Адміністратор" else None
        print("Натискання 'Sign In' з роллю:", role)
        try:
            self.on_login(role, password)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            print("Помилка входу:", str(e))
