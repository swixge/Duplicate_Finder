import tkinter as tk
from tkinter import messagebox, ttk
import os


class HistoryWindow:
    """Singleton history window - opens once and reuses"""
    
    _instance = None
    
    def __new__(cls, parent, controller):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, parent, controller):
        if self._initialized:
            # Window already exists, just refresh it
            self.refresh_data()
            self.window.lift()  # Bring to front
            self.window.focus()
            return
        
        self._initialized = True
        self.parent = parent
        self.controller = controller
        self.window = None
        self.tree = None
        self.stats_window = None
        
        self._create_window()
    
    def _create_window(self):
        """Create the history window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📜 Search History")
        self.window.geometry("1100x550")
        self.window.configure(bg="#0a0e27")
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Style
        style = ttk.Style()
        style.configure("Premium.Treeview", background="#0f1535", foreground="#ffffff",
                       fieldbackground="#0f1535", borderwidth=0)
        style.configure("Premium.Treeview.Heading", background="#1a1f3a", foreground="#00d4ff")
        
        # Title frame
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ttk.Label(title_frame, text="📜 Search History", font=("Arial", 14, "bold"))
        title_label.pack(side="left")
        
        refresh_btn = ttk.Button(title_frame, text="🔄 Refresh", command=self.refresh_data)
        refresh_btn.pack(side="right", padx=5)
        
        # Create treeview
        self.tree = ttk.Treeview(
            self.window,
            columns=("ID", "File", "User", "Date", "Chars", "Words", "Unique"),
            show="headings",
            height=15,
            style="Premium.Treeview"
        )
        
        columns_config = [
            ("ID", 50),
            ("File", 300),
            ("User", 100),
            ("Date", 150),
            ("Chars", 80),
            ("Words", 80),
            ("Unique", 100)
        ]
        
        for col_name, width in columns_config:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="📊 Show Stats", command=self._show_stats).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self._delete_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Close", command=self._on_close).pack(side="right", padx=5)
        
        # Populate data
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the data in the tree"""
        if self.tree is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load new data
        files = self.controller.get_all_files()
        if not files:
            messagebox.showinfo("History", "No previous searches")
            return
        
        for file_data in files:
            file_id, path, user, date, char_count, word_count, unique_words, *_ = file_data
            self.tree.insert("", tk.END, values=(
                file_id,
                os.path.basename(path),
                user,
                date,
                char_count,
                word_count,
                unique_words
            ))
    
    def _show_stats(self):
        """Show statistics for selected file"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a file")
            return
        
        file_id = self.tree.item(selected)["values"][0]
        stats = self.controller.get_file_stats(file_id)
        file_info = self.controller.get_file_info(file_id)
        
        if not stats:
            messagebox.showinfo("Info", "No results for this file")
            return
        
        # Close previous stats window if open
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.destroy()
        
        self._create_stats_window(file_id, stats, file_info)
    
    def _create_stats_window(self, file_id, stats, file_info):
        """Create stats window"""
        self.stats_window = tk.Toplevel(self.window)
        self.stats_window.title(f"📊 File Statistics #{file_id}")
        self.stats_window.geometry("1100x650")
        self.stats_window.configure(bg="#0a0e27")
        
        # Info text
        info_text = "No data"
        if file_info:
            info_text = (f"📊 {file_info['char_count']} chars | 📝 {file_info['word_count']} words | "
                        f"🎯 {file_info['unique_words']} unique | 📏 {file_info['avg_word_length']:.2f} avg")
        
        info_label = ttk.Label(self.stats_window, text=info_text, font=("Arial", 10))
        info_label.pack(fill="x", padx=10, pady=5)
        
        # Style
        style = ttk.Style()
        style.configure("Premium.Treeview", background="#0f1535", foreground="#ffffff",
                       fieldbackground="#0f1535", borderwidth=0)
        style.configure("Premium.Treeview.Heading", background="#1a1f3a", foreground="#00d4ff")
        
        # Stats tree
        stats_tree = ttk.Treeview(
            self.stats_window,
            columns=("Algorithm", "Duplicates", "Unique", "Frequency", "Time", "Top", "Count", "Percentage"),
            show="headings",
            style="Premium.Treeview"
        )
        
        columns_config = [
            ("Algorithm", 120),
            ("Duplicates", 80),
            ("Unique", 80),
            ("Frequency", 80),
            ("Time", 70),
            ("Top", 250),
            ("Count", 100),
            ("Percentage", 100)
        ]
        
        for col_name, width in columns_config:
            stats_tree.heading(col_name, text=col_name)
            stats_tree.column(col_name, width=width)
        
        stats_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Populate stats
        for algo, data in stats.items():
            top_phrases = "; ".join([phrase for phrase, _ in data["top_phrases"][:5]])
            counts = "; ".join([str(count) for _, count in data["top_phrases"][:5]])
            stats_tree.insert("", tk.END, values=(
                algo,
                data["duplicates"],
                data["unique_count"],
                data["frequency"],
                f"{data['time']:.4f}",
                top_phrases,
                counts,
                f"{data['repeat_percentage']:.2f}%"
            ))
    
    def _delete_file(self):
        """Delete selected file"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a file")
            return
        
        if messagebox.askyesno("Confirm", "Delete this search?"):
            file_id = self.tree.item(selected)["values"][0]
            self.controller.delete_file(file_id)
            self.tree.delete(selected)
            messagebox.showinfo("Success", "Search deleted")
    
    def _on_close(self):
        """Handle window close"""
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.destroy()
        
        self.window.destroy()
        self._initialized = False
        HistoryWindow._instance = None
    
    def show(self):
        """Show the window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus()
        else:
            self._initialized = False
            HistoryWindow._instance = None
