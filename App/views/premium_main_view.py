import threading
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from models import FileProcessor
import time
from .history_window import HistoryWindow

try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except ImportError:
    HAS_CUSTOMTKINTER = False


class PremiumMainView:
    """Premium main view with 2025 design trends - glassmorphism, gradients, animations"""

    def __init__(self, root, controller):
        print("Ініціалізація PremiumMainView")
        self.root = root
        self.controller = controller
        self.root.title("Duplicate Finder - Premium Edition")
        self.root.geometry("1600x950")
        self.root.minsize(1200, 800)
        
        if HAS_CUSTOMTKINTER:
            self._setup_premium_ui()
        else:
            from .modern_main_view import ModernMainView
            old_view = ModernMainView(root, controller)
            self.__dict__.update(old_view.__dict__)

    def _update_ui_after_analysis(self, results):
            """Оновлення інтерфейсу після аналізу"""
            # Очищаємо таблицю від старих результатів
            self.result_table.delete(*self.result_table.get_children())
        
            # Заповнюємо таблицю новими результатами
            for algo, data in results.items():
                # Формуємо рядки з топ-фразами
                top_phrases = "; ".join([f"{phrase}" for phrase, count in data.get("top_phrases", [])[:5]])
                counts = "; ".join([f"{count}" for phrase, count in data.get("top_phrases", [])[:5]])
            
                # Додаємо рядок у таблицю
                self.result_table.insert("", tk.END, values=(
                    algo,
                    data.get("duplicates", 0),
                    data.get("unique_count", 0),
                    data.get("frequency", 0),
                    f"{data.get('time', 0):.4f}",
                    top_phrases,
                    counts,
                    f"{data.get('repeat_percentage', 0):.2f}%"
                ))
        
            # Підсвітка дублікатів у тексті
            if results:
                try:
                    self.highlight_duplicates(
                        self.text_display, 
                        results, 
                        int(self.window_size_entry.get() or 5)
                    )
                except Exception as e:
                    print(f"Помилка підсвітки тексту: {e}")
            else:
                messagebox.showwarning("Попередження", "Дублікатів не знайдено")

    def _setup_premium_ui(self):
        """Setup premium UI with 2025 design trends"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main container with gradient effect
        main_container = ctk.CTkFrame(self.root, fg_color="#0a0e27")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header with glassmorphism
        self._create_premium_header(main_container)
        
        # Content area
        content_area = ctk.CTkFrame(main_container, fg_color="#0a0e27")
        content_area.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Sidebar with gradient
        self._create_premium_sidebar(content_area)
        
        # Main content with cards
        self._create_premium_content(content_area)

    def _create_premium_header(self, parent):
        """Create premium header with glassmorphism effect"""
        header = ctk.CTkFrame(parent, fg_color="#0f1535", height=100)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Decorative gradient line
        accent_line = ctk.CTkFrame(header, fg_color="#00d4ff", height=3)
        accent_line.pack(fill="x", padx=0, pady=0)
        
        # Title with icon
        title_label = ctk.CTkLabel(
            header,
            text="✨ Duplicate Finder Premium",
            font=("Helvetica", 28, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left", padx=30, pady=20)
        
        # Info label
        self.file_info_label = ctk.CTkLabel(
            header,
            text="📄 No file loaded",
            font=("Helvetica", 11),
            text_color="#a0d4ff"
        )
        self.file_info_label.pack(side="right", padx=30, pady=20)

    def _create_premium_sidebar(self, parent):
        """Create premium sidebar with gradient and modern buttons"""
        sidebar = ctk.CTkFrame(parent, fg_color="#0f1535", width=220)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Accent line
        accent = ctk.CTkFrame(sidebar, fg_color="#ff006e", width=4)
        accent.pack(side="left", fill="y", padx=0, pady=0)
        
        # Content frame
        content = ctk.CTkFrame(sidebar, fg_color="#0f1535")
        content.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Logo
        logo_label = ctk.CTkLabel(
            content,
            text="🔍",
            font=("Helvetica", 50),
            text_color="#00d4ff"
        )
        logo_label.pack(pady=20)
        
        # Premium buttons with gradient-like effect
        button_configs = [
            ("📁 Load File", self.load_file, "#00d4ff", "#00a8cc"),
            ("⚙️ Analyze", self.analyze, "#00d4ff", "#00a8cc"),
            ("📜 History", self.show_previous, "#ff006e", "#cc0055"),
        ]
        
        for text, command, fg_color, hover_color in button_configs:
            btn = ctk.CTkButton(
                content,
                text=text,
                command=command,
                font=("Helvetica", 12, "bold"),
                height=50,
                corner_radius=12,
                fg_color=fg_color,
                hover_color=hover_color,
                text_color="#0a0e27",
                border_width=0
            )
            btn.pack(fill="x", padx=15, pady=8)
        
        # Separator
        separator = ctk.CTkFrame(content, fg_color="#1a1f3a", height=2)
        separator.pack(fill="x", padx=15, pady=20)
        
        # Algorithm selection
        algo_label = ctk.CTkLabel(
            content,
            text="Select Algorithm",
            font=("Helvetica", 11, "bold"),
            text_color="#ffffff"
        )
        algo_label.pack(padx=15, pady=(10, 5))
        
        self.algorithm_var = tk.StringVar(value="All")
        
        algo_options = [
            ("All Algorithms", "All"),
            ("🔴 Rabin-Karp", "Рабін-Карп"),
            ("🟢 Suffix Tree", "Суфіксні дерева"),
            ("🔵 Semantic", "Семантичний"),
            ("🔴 Fuzzy Match", "Нечіткий пошук"),
            ("🟢 N-gram Analysis", "N-грам аналіз")
        ]
        
        for text, value in algo_options:
            radio = ctk.CTkRadioButton(
                content,
                text=text,
                variable=self.algorithm_var,
                value=value,
                font=("Helvetica", 10),
                text_color="#ffffff"
            )
            radio.pack(anchor="w", padx=25, pady=3)
        
        # Separator
        sep = ctk.CTkFrame(content, fg_color="#1a1f3a", height=2)
        sep.pack(fill="x", padx=15, pady=10)
        
        # Window size input
        size_label = ctk.CTkLabel(
            content,
            text="Substring Length",
            font=("Helvetica", 11, "bold"),
            text_color="#ffffff"
        )
        size_label.pack(padx=15, pady=(10, 5))
        
        self.window_size_entry = ctk.CTkEntry(
            content,
            placeholder_text="5",
            font=("Helvetica", 11),
            height=40,
            border_width=2,
            border_color="#00d4ff",
            fg_color="#1a1f3a",
            text_color="#ffffff"
        )
        self.window_size_entry.pack(fill="x", padx=15, pady=(0, 20))
        self.window_size_entry.insert(0, "5")
        
        # Logout button
        logout_btn = ctk.CTkButton(
            content,
            text="🚪 Sign Out",
            command=self.logout,
            font=("Helvetica", 12, "bold"),
            height=45,
            corner_radius=12,
            fg_color="#ff006e",
            hover_color="#cc0055",
            text_color="#ffffff",
            border_width=0
        )
        logout_btn.pack(fill="x", padx=15, pady=10, side="bottom")

    def _create_premium_content(self, parent):
        """Create premium content area with card-based design"""
        content = ctk.CTkFrame(parent, fg_color="#0a0e27")
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Results card
        self._create_results_card(content)
        
        # Text display card
        self._create_text_display_card(content)

    def _create_results_card(self, parent):
        """Create results card with glassmorphism"""
        card_label = ctk.CTkLabel(
            parent,
            text="📊 Analysis Results",
            font=("Helvetica", 14, "bold"),
            text_color="#00d4ff"
        )
        card_label.pack(anchor="w", pady=(0, 10))
        
        card = ctk.CTkFrame(parent, fg_color="#0f1535", corner_radius=15, border_width=2, border_color="#1a1f3a")
        card.pack(fill="x", pady=(0, 15))
        
        # Create treeview with premium styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Premium.Treeview", background="#0f1535", foreground="#ffffff",
                       fieldbackground="#0f1535", borderwidth=0, font=("Helvetica", 10))
        style.configure("Premium.Treeview.Heading", background="#1a1f3a", foreground="#00d4ff",
                       font=("Helvetica", 10, "bold"), borderwidth=1)
        style.map("Premium.Treeview", background=[("selected", "#00d4ff")])
        style.map("Premium.Treeview.Heading", background=[("active", "#1a1f3a")])
        
        self.result_table = ttk.Treeview(
            card,
            columns=("Algorithm", "Duplicates", "Unique", "Frequency", "Time", "Top Phrases", "Count", "Percentage"),
            show="headings",
            height=5,
            style="Premium.Treeview"
        )
        
        columns_config = [
            ("Algorithm", 120),
            ("Duplicates", 80),
            ("Unique", 80),
            ("Frequency", 80),
            ("Time", 70),
            ("Top Phrases", 250),
            ("Count", 100),
            ("Percentage", 100)
        ]
        
        for col_name, width in columns_config:
            self.result_table.heading(col_name, text=col_name)
            self.result_table.column(col_name, width=width)
        
        self.result_table.pack(fill="x", padx=15, pady=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(card, orient="horizontal", command=self.result_table.xview)
        scrollbar.pack(fill="x", padx=15, pady=(0, 15))
        self.result_table.configure(xscrollcommand=scrollbar.set)

    def _create_text_display_card(self, parent):
        """Create text display card with premium styling"""
        text_label = ctk.CTkLabel(
            parent,
            text="📄 Document Content",
            font=("Helvetica", 14, "bold"),
            text_color="#00d4ff"
        )
        text_label.pack(anchor="w", pady=(0, 10))
        
        card = ctk.CTkFrame(parent, fg_color="#0f1535", corner_radius=15, border_width=2, border_color="#1a1f3a")
        card.pack(fill="both", expand=True)
        
        self.text_display = tk.Text(
            card,
            wrap="word",
            font=("Courier", 10),
            bg="#0a0e27",
            fg="#ffffff",
            insertbackground="#00d4ff",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=15,
            selectbackground="#00d4ff",
            selectforeground="#0a0e27"
        )
        self.text_display.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.text_display.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)
        self.text_display.configure(yscrollcommand=scrollbar.set)

    def load_file(self):
        """Load file dialog"""
        self.result_table.delete(*self.result_table.get_children())
        self.text_display.delete(1.0, tk.END)
        print("Виклик load_file у PremiumMainView")
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")])
        if file_path:
            try:
                print(f"Обрано файл: {file_path}")
                self.controller.load_file(file_path)
                print("Файл успішно оброблено контролером")
                messagebox.showinfo("Success", f"✅ File loaded: {os.path.basename(file_path)}")
                self.result_table.delete(*self.result_table.get_children())
                self.text_display.delete(1.0, tk.END)
                self.display_formatted_text(self.text_display, self.controller.file_text)
                self.update_file_info_label(self.file_info_label, self.controller.file_text_stats)
            except Exception as e:
                error_msg = f"Error loading file: {str(e)}"
                print(error_msg)
                messagebox.showerror("Error", error_msg)

    def display_formatted_text(self, text_widget, formatted_text):
        """Display formatted text with all formatting preserved"""
        # Configure formatting tags
        text_widget.tag_configure("bold", font=("Courier", 10, "bold"))
        text_widget.tag_configure("italic", font=("Courier", 10, "italic"))
        text_widget.tag_configure("underline", underline=True)
        
        if isinstance(formatted_text, list):
            current_pos = 1.0
            for segment in formatted_text:
                text = segment["text"]
                start_idx = text_widget.index(current_pos)
                text_widget.insert(current_pos, text)
                end_idx = text_widget.index(f"{current_pos} + {len(text)}c")
                
                # Apply formatting
                fmt = segment.get("format", {})
                if fmt.get("bold", False):
                    text_widget.tag_add("bold", start_idx, end_idx)
                if fmt.get("italic", False):
                    text_widget.tag_add("italic", start_idx, end_idx)
                if fmt.get("underline", False):
                    text_widget.tag_add("underline", start_idx, end_idx)
                
                # Apply font size if available
                if fmt.get("size"):
                    size_tag = f"size_{int(fmt['size'])}"
                    if size_tag not in text_widget.tag_names():
                        text_widget.tag_configure(size_tag, font=("Courier", int(fmt["size"])))
                    text_widget.tag_add(size_tag, start_idx, end_idx)
                
                # Apply font color if available
                if fmt.get("color"):
                    color_tag = f"color_{fmt['color']}"
                    if color_tag not in text_widget.tag_names():
                        try:
                            text_widget.tag_configure(color_tag, foreground=fmt["color"])
                        except:
                            pass  # Skip if color format is invalid
                    text_widget.tag_add(color_tag, start_idx, end_idx)
                
                current_pos = end_idx
        else:
            text_widget.insert(1.0, formatted_text)

    def update_file_info_label(self, label, stats):
        """Update file info label"""
        if not stats:
            label.configure(text="📄 No file loaded")
            return
        info = (f"📊 {stats['char_count']} chars | 📝 {stats['word_count']} words | "
                f"🎯 {stats['unique_words']} unique | 📏 {stats['avg_word_length']:.2f} avg length")
        label.configure(text=info)

    def analyze(self):
        """Запуск аналізу в окремому потоці з прогрес-баром"""
        if not hasattr(self.controller, 'file_path') or not self.controller.file_path:
            messagebox.showwarning("Попередження", "Спочатку завантажте файл")
            return

        try:
            window_size = int(self.window_size_entry.get() or 5)
            self.controller.set_window_size(window_size)
            
            selected_algo = self.algorithm_var.get()
            algorithm = None if selected_algo == "All" else selected_algo

            # Створюємо прогрес-бар
            self.progress_bar = ctk.CTkProgressBar(self.root)
            self.progress_bar.pack(fill="x", padx=30, pady=10)
            self.progress_bar.set(0.05)

            # Блокування кнопок
            self._set_buttons_state("disabled")

            def analysis_task():
                try:
                    self.progress_bar.set(0.2)
                    results = self.controller.analyze(algorithm=algorithm)
                    self.progress_bar.set(0.75)
                    
                    # Оновлюємо інтерфейс у головному потоці
                    self.root.after(0, lambda: self._finish_analysis(results))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Помилка аналізу", str(e)))
                finally:
                    self.root.after(0, self._cleanup_after_analysis)

            # Запускаємо в окремому потоці
            threading.Thread(target=analysis_task, daemon=True).start()

        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне число для довжини підрядка")
        except Exception as e:
            messagebox.showerror("Помилка", f"Непередбачена помилка: {str(e)}")


    def _finish_analysis(self, results):
        """Оновлення інтерфейсу після успішного аналізу"""
        # Очищаємо таблицю
        self.result_table.delete(*self.result_table.get_children())
        
        # Заповнюємо таблицю новими результатами
        for algo, data in results.items():
            top_phrases_str = "; ".join([f"{phrase}" for phrase, count in data.get("top_phrases", [])[:5]])
            counts_str = "; ".join([f"{count}" for phrase, count in data.get("top_phrases", [])[:5]])
            
            self.result_table.insert("", tk.END, values=(
                algo,
                data.get("duplicates", 0),
                data.get("unique_count", 0),
                data.get("frequency", 0),
                f"{data.get('time', 0):.4f}",
                top_phrases_str,
                counts_str,
                f"{data.get('repeat_percentage', 0):.2f}%"
            ))

        # Підсвітка тексту
        if results:
            try:
                self.highlight_duplicates(
                    self.text_display, 
                    results, 
                    int(self.window_size_entry.get() or 5)
                )
            except Exception as e:
                print(f"Помилка підсвітки тексту: {e}")


    def _cleanup_after_analysis(self):
        """Прибирання після аналізу"""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            try:
                self.progress_bar.destroy()
            except:
                pass
        self._set_buttons_state("normal")


    def _set_buttons_state(self, state: str):
        """Блокування/розблокування кнопок під час аналізу"""
        # Поки що порожньо. Можна пізніше додати реальне блокування кнопок
        pass

    def highlight_duplicates(self, text_widget, results, window_size):
        """ПІДСВІТКА ВСЬОГО, ЩО ЗНАЙШЛИ АЛГОРИТМИ — максимально проста і стабільна версія"""
        if not results or not isinstance(results, dict):
            return

        # Очищаємо старі теги
        for tag in list(text_widget.tag_names()):
            if tag.startswith("highlight_"):
                text_widget.tag_remove(tag, "1.0", tk.END)

        # Повний текст
        if isinstance(self.controller.file_text, list):
            full_text = "".join(segment.get("text", "") for segment in self.controller.file_text)
        else:
            full_text = str(self.controller.file_text)

        if not full_text:
            return

        # Кольори
        colors = {
            "Рабін-Карп": "#FF6B6B",
            "Суфіксні дерева": "#4ECDC4",
            "Семантичний": "#45B7D1",
            "Нечіткий пошук": "#FFD93D",
            "N-грам аналіз": "#A8E6CF"
        }

        for algo, color in colors.items():
            text_widget.tag_configure(f"highlight_{algo}", background=color, foreground="#000000", font=("Courier", 10, "bold"))

        total = 0
        covered = set()

        for algo, data in results.items():
            if not isinstance(data, dict):
                continue

            # 1. duplicates (головне джерело)
            duplicates = data.get("duplicates", {})
            if isinstance(duplicates, dict):
                for phrase, pos_list in duplicates.items():
                    phrase = str(phrase).strip()
                    if not phrase:
                        continue
                    if not isinstance(pos_list, list):
                        pos_list = [pos_list] if isinstance(pos_list, (int, float)) else []
                    for start in pos_list:
                        if not isinstance(start, (int, float)):
                            continue
                        start = int(start)
                        end = start + len(phrase)
                        if any(s <= start < e or s < end <= e for s, e in covered):
                            continue
                        try:
                            text_widget.tag_add(f"highlight_{algo}", f"1.0 + {start} chars", f"1.0 + {end} chars")
                            covered.add((start, end))
                            total += 1
                        except:
                            pass

            # 2. positions
            positions = data.get("positions", {})
            if isinstance(positions, dict):
                for phrase, pos_list in positions.items():
                    phrase = str(phrase).strip()
                    if not phrase:
                        continue
                    if not isinstance(pos_list, list):
                        pos_list = [pos_list] if isinstance(pos_list, (int, float)) else []
                    for start in pos_list:
                        if not isinstance(start, (int, float)):
                            continue
                        start = int(start)
                        end = start + len(phrase)
                        if any(s <= start < e or s < end <= e for s, e in covered):
                            continue
                        try:
                            text_widget.tag_add(f"highlight_{algo}", f"1.0 + {start} chars", f"1.0 + {end} chars")
                            covered.add((start, end))
                            total += 1
                        except:
                            pass

            # 3. top_phrases (fallback)
            for item in data.get("top_phrases", []):
                phrase = str(item[0] if isinstance(item, (list, tuple)) else item).strip()
                if not phrase:
                    continue
                start_pos = 0
                while True:
                    pos = full_text.lower().find(phrase.lower(), start_pos)
                    if pos == -1:
                        break
                    end = pos + len(phrase)
                    if any(s <= pos < e or s < end <= e for s, e in covered):
                        start_pos = pos + 1
                        continue
                    try:
                        text_widget.tag_add(f"highlight_{algo}", f"1.0 + {pos} chars", f"1.0 + {end} chars")
                        covered.add((pos, end))
                        total += 1
                    except:
                        pass
                    start_pos = pos + 1

        print(f"Підсвітка завершена. Виділено {total} фраз")

    def show_previous(self):
        """Show previous searches using singleton window"""
        if not self.controller.is_admin:
            messagebox.showerror("Error", "Admin access required")
            return
        
        # Use singleton history window
        history_window = HistoryWindow(self.root, self.controller)
        history_window.show()


    def logout(self):
        """Logout"""
        print("Signing out")
        self.controller.cleanup()
        self.root.destroy()
