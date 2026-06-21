import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False

from .history_window import HistoryWindow


class PremiumMainView:
    """Головне вікно з преміум-дизайном, підсвіткою та повним функціоналом."""

    COLORS = {
        "Рабін-Карп":      "#FF6B6B",
        "Суфіксні дерева": "#4ECDC4",
        "Семантичний":     "#45B7D1",
        "Нечіткий пошук":  "#FFD93D",
        "N-грам аналіз":   "#A8E6CF",
    }

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Duplicate Finder – Premium Edition")
        self.root.geometry("1400x850")
        self.root.minsize(800, 500)

        if HAS_CTK:
            self._build_ui()
        else:
            messagebox.showwarning(
                "Увага",
                "Бібліотека customtkinter не знайдена.\n"
                "Встановіть її: pip install customtkinter"
            )
            self._build_fallback_ui()

    # ══════════════════════════════════════════════════════════════════════════
    # ПОБУДОВА ІНТЕРФЕЙСУ
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        root_frame = ctk.CTkFrame(self.root, fg_color="#0a0e27")
        root_frame.pack(fill="both", expand=True)

        self._create_header(root_frame)

        body = ctk.CTkFrame(root_frame, fg_color="#0a0e27")
        body.pack(fill="both", expand=True)

        self._create_sidebar(body)
        self._create_main_area(body)

    def _create_header(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="#0f1535", height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkFrame(hdr, fg_color="#00d4ff", height=3).pack(fill="x")

        ctk.CTkLabel(
            hdr, text="✨ Duplicate Finder Premium",
            font=("Helvetica", 24, "bold"), text_color="#ffffff"
        ).pack(side="left", padx=30, pady=15)

        self.file_info_label = ctk.CTkLabel(
            hdr, text="📄 Файл не завантажено",
            font=("Helvetica", 11), text_color="#a0d4ff"
        )
        self.file_info_label.pack(side="right", padx=30, pady=15)

    def _create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color="#0f1535", width=235)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Вертикальна акцентна смуга
        ctk.CTkFrame(sidebar, fg_color="#ff006e", width=4).pack(side="left", fill="y")

        # Кнопка «Вийти» закріплена знизу — поза scrollable-зоною
        bottom_bar = ctk.CTkFrame(sidebar, fg_color="#0f1535", height=58)
        bottom_bar.pack(side="bottom", fill="x")
        bottom_bar.pack_propagate(False)
        ctk.CTkButton(
            bottom_bar, text="🚪  Вийти", command=self.logout,
            font=("Helvetica", 11, "bold"), height=40, corner_radius=8,
            fg_color="#ff006e", hover_color="#cc0055", text_color="#ffffff",
        ).pack(fill="x", padx=12, pady=8)

        # Увесь контент — скролюється
        content = ctk.CTkScrollableFrame(
            sidebar, fg_color="#0f1535",
            scrollbar_button_color="#1a1f3a",
            scrollbar_button_hover_color="#00d4ff",
        )
        content.pack(fill="both", expand=True)

        ctk.CTkLabel(content, text="🔍", font=("Helvetica", 36), text_color="#00d4ff").pack(pady=10)

        # ── Основні кнопки ──────────────────────────────────────────────
        self._btn(content, "📁  Завантажити файл", self.load_file, "#00d4ff", "#00a8cc")
        self._btn(content, "⚙️  Аналізувати",      self.analyze,   "#00d4ff", "#00a8cc")

        self._separator(content)

        # ── Вибір алгоритму ─────────────────────────────────────────────
        ctk.CTkLabel(content, text="Алгоритм", font=("Helvetica", 11, "bold"),
                     text_color="#ffffff").pack(pady=(6, 2))

        self.algorithm_var = tk.StringVar(value="All")
        for label, value in [
            ("Всі алгоритми",      "All"),
            ("🔴 Рабін-Карп",      "Рабін-Карп"),
            ("🟢 Суфіксні дерева", "Суфіксні дерева"),
            ("🔵 Семантичний",     "Семантичний"),
            ("🟡 Нечіткий пошук",  "Нечіткий пошук"),
            ("🟩 N-грам аналіз",   "N-грам аналіз"),
        ]:
            ctk.CTkRadioButton(
                content, text=label, variable=self.algorithm_var, value=value,
                font=("Helvetica", 10), text_color="#ffffff"
            ).pack(anchor="w", padx=18, pady=2)

        self._separator(content)

        # ── Довжина підрядка ─────────────────────────────────────────────
        ctk.CTkLabel(content, text="Довжина підрядка", font=("Helvetica", 11, "bold"),
                     text_color="#ffffff").pack(pady=(6, 2))
        self.window_size_entry = ctk.CTkEntry(
            content, placeholder_text="5",
            height=36, border_width=2, border_color="#00d4ff",
            fg_color="#1a1f3a", text_color="#ffffff"
        )
        self.window_size_entry.pack(fill="x", padx=12)
        self.window_size_entry.insert(0, "5")

        self._separator(content)

        # ── Інструменти ──────────────────────────────────────────────────
        ctk.CTkLabel(content, text="Інструменти", font=("Helvetica", 11, "bold"),
                     text_color="#ffffff").pack(pady=(6, 2))
        self._btn(content, "🌐  HTML-підсвітка",  self.open_html,     "#6c63ff", "#5a52d5")
        self._btn(content, "💾  Зберегти JSON",   self.export_json,   "#28a745", "#1e7e34")
        self._btn(content, "📝  Зберегти звіт",  self.export_txt,    "#28a745", "#1e7e34")
        self._btn(content, "📜  Історія",         self.show_previous, "#ff006e", "#cc0055")

        # Нижній відступ щоб останній елемент не впирався у scrollbar
        ctk.CTkFrame(content, fg_color="transparent", height=12).pack()

    def _create_main_area(self, parent):
        area = ctk.CTkFrame(parent, fg_color="#0a0e27")
        area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self._create_results_panel(area)
        self._create_text_panel(area)

    def _create_results_panel(self, parent):
        ctk.CTkLabel(parent, text="📊 Результати аналізу",
                     font=("Helvetica", 14, "bold"), text_color="#00d4ff"
                     ).pack(anchor="w", pady=(0, 6))

        card = ctk.CTkFrame(parent, fg_color="#0f1535", corner_radius=12,
                             border_width=1, border_color="#1a1f3a")
        card.pack(fill="x", pady=(0, 12))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("P.Treeview",
                        background="#0f1535", foreground="#ffffff",
                        fieldbackground="#0f1535", font=("Helvetica", 10))
        style.configure("P.Treeview.Heading",
                        background="#1a1f3a", foreground="#00d4ff",
                        font=("Helvetica", 10, "bold"))
        style.map("P.Treeview", background=[("selected", "#00d4ff")],
                  foreground=[("selected", "#000000")])

        cols = ("Алгоритм", "Дублікатів", "Унікальних", "Частота",
                "Час(с)", "Топ-фрази", "К-сть", "%")
        self.result_table = ttk.Treeview(card, columns=cols, show="headings",
                                          height=5, style="P.Treeview")

        widths = (130, 90, 90, 80, 70, 320, 80, 80)
        for col, w in zip(cols, widths):
            self.result_table.heading(col, text=col)
            self.result_table.column(col, width=w, minwidth=w)
        self.result_table.pack(fill="x", padx=12, pady=12)

        # Контекстне меню (правий клік → копіювати рядок)
        self.result_table.bind("<Button-3>", self._on_table_right_click)

        hbar = ttk.Scrollbar(card, orient="horizontal", command=self.result_table.xview)
        hbar.pack(fill="x", padx=12, pady=(0, 8))
        self.result_table.configure(xscrollcommand=hbar.set)

    def _create_text_panel(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(hdr, text="📄 Вміст документа",
                     font=("Helvetica", 14, "bold"), text_color="#00d4ff"
                     ).pack(side="left")

        # Кнопка «Очистити»
        ctk.CTkButton(
            hdr, text="✖ Очистити", width=100, height=28,
            corner_radius=6, fg_color="#ff006e", hover_color="#cc0055",
            text_color="#ffffff", command=self._clear_text
        ).pack(side="right")

        card = ctk.CTkFrame(parent, fg_color="#0f1535", corner_radius=12,
                             border_width=1, border_color="#1a1f3a")
        card.pack(fill="both", expand=True)

        self.text_display = tk.Text(
            card, wrap="word", font=("Courier", 10),
            bg="#0a0e27", fg="#e0e0e0", insertbackground="#00d4ff",
            relief="flat", borderwidth=0, padx=14, pady=14,
            selectbackground="#00d4ff", selectforeground="#000000"
        )
        self.text_display.pack(fill="both", expand=True, padx=12, pady=12)

        vbar = ttk.Scrollbar(card, orient="vertical", command=self.text_display.yview)
        vbar.pack(side="right", fill="y", padx=(0, 12), pady=12)
        self.text_display.configure(yscrollcommand=vbar.set)

    # ══════════════════════════════════════════════════════════════════════════
    # ПОДІЇ / КНОПКИ
    # ══════════════════════════════════════════════════════════════════════════

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Оберіть файл",
            filetypes=[("PDF/DOCX", "*.pdf *.docx"), ("PDF", "*.pdf"), ("Word", "*.docx")]
        )
        if not file_path:
            return
        try:
            self.controller.load_file(file_path)
            self.result_table.delete(*self.result_table.get_children())
            self.text_display.delete("1.0", tk.END)
            self._display_text(self.controller.file_text)
            self._update_file_info(self.controller.file_text_stats)
            messagebox.showinfo("Успішно", f"✅ Файл завантажено:\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Помилка завантаження", str(e))

    def analyze(self):
        if not self.controller.file_path:
            messagebox.showwarning("Попередження", "Спочатку завантажте файл.")
            return

        try:
            ws = int(self.window_size_entry.get() or 5)
            self.controller.set_window_size(ws)
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне ціле число для довжини підрядка.")
            return

        algo_sel = self.algorithm_var.get()
        algorithm = None if algo_sel == "All" else algo_sel

        # Прогрес-бар
        self.progress = ctk.CTkProgressBar(self.root)
        self.progress.pack(fill="x", padx=30, pady=6)
        self.progress.set(0.05)
        self._set_ui_state("disabled")

        def _task():
            try:
                self.progress.set(0.25)
                results = self.controller.analyze(algorithm=algorithm)
                self.progress.set(0.80)
                self.root.after(0, lambda: self._finish_analysis(results))
            except Exception as exc:
                self.root.after(0, lambda: messagebox.showerror("Помилка аналізу", str(exc)))
            finally:
                self.root.after(0, self._cleanup_progress)

        threading.Thread(target=_task, daemon=True).start()

    def _finish_analysis(self, results: dict):
        self.result_table.delete(*self.result_table.get_children())

        for algo, data in results.items():
            phrases_str = "; ".join(p for p, _ in data.get("top_phrases", [])[:5])
            counts_str  = "; ".join(str(c) for _, c in data.get("top_phrases", [])[:5])
            self.result_table.insert("", tk.END, values=(
                algo,
                data.get("duplicates", 0),
                data.get("unique_count", 0),
                data.get("frequency", 0),
                f"{data.get('time', 0):.4f}",
                phrases_str,
                counts_str,
                f"{data.get('repeat_percentage', 0):.2f}%",
            ))

        try:
            ws = int(self.window_size_entry.get() or 5)
            self.highlight_duplicates(results, ws)
        except Exception as e:
            print(f"Помилка підсвітки: {e}")

        if not results or all(d.get("duplicates", 0) == 0 for d in results.values()):
            messagebox.showinfo("Результат", "Дублікатів не знайдено у цьому документі.")

    def _cleanup_progress(self):
        if hasattr(self, "progress") and self.progress:
            try:
                self.progress.destroy()
            except Exception:
                pass
        self._set_ui_state("normal")

    def open_html(self):
        """Генерує HTML із підсвіткою та відкриває у браузері."""
        if not self.controller.file_results:
            messagebox.showwarning("Попередження", "Спочатку запустіть аналіз.")
            return
        try:
            text = self.controller.get_plain_text()
            ws = int(self.window_size_entry.get() or 5)
            html_path = self.controller.generate_highlighted_html(
                text, self.controller.file_results, ws
            )
            if html_path:
                self.controller.open_highlighted_file(html_path)
            else:
                messagebox.showwarning("Увага", "HTML-файл не створено (текст або результати порожні).")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def export_json(self):
        if not self.controller.file_results:
            messagebox.showwarning("Попередження", "Спочатку запустіть аналіз.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файли", "*.json")],
            title="Зберегти результати JSON"
        )
        if not path:
            return
        try:
            saved = self.controller.export_results_json(path)
            messagebox.showinfo("Збережено", f"✅ JSON збережено:\n{saved}")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def export_txt(self):
        if not self.controller.file_results:
            messagebox.showwarning("Попередження", "Спочатку запустіть аналіз.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt")],
            title="Зберегти текстовий звіт"
        )
        if not path:
            return
        try:
            saved = self.controller.export_results_txt(path)
            messagebox.showinfo("Збережено", f"✅ Звіт збережено:\n{saved}")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def show_previous(self):
        if not self.controller.is_admin:
            messagebox.showerror("Помилка доступу", "Тільки для адміністратора.")
            return
        HistoryWindow(self.root, self.controller).show()

    def logout(self):
        self.controller.cleanup()
        self.root.destroy()

    def _clear_text(self):
        self.text_display.delete("1.0", tk.END)
        self.result_table.delete(*self.result_table.get_children())
        # Скидаємо теги підсвітки
        for tag in list(self.text_display.tag_names()):
            if tag.startswith("hl_"):
                self.text_display.tag_delete(tag)
        self.file_info_label.configure(text="📄 Файл не завантажено")

    # ══════════════════════════════════════════════════════════════════════════
    # ПІДСВІТКА ДУБЛІКАТІВ У ТЕКСТІ
    # ══════════════════════════════════════════════════════════════════════════

    def highlight_duplicates(self, results: dict, window_size: int):
        """Підсвічує всі знайдені дублікати у text_display."""
        tw = self.text_display

        # Видаляємо старі теги підсвітки
        for tag in list(tw.tag_names()):
            if tag.startswith("hl_"):
                try:
                    tw.tag_remove(tag, "1.0", tk.END)
                except Exception:
                    pass

        full_text = self.controller.get_plain_text()
        if not full_text:
            return

        # Конфігуруємо теги
        for algo, color in self.COLORS.items():
            tag = f"hl_{algo}"
            tw.tag_configure(tag, background=color, foreground="#000000",
                             font=("Courier", 10, "bold"))

        # Збираємо відрізки (start, end) для кожного алгоритму
        covered: set[tuple[int, int]] = set()
        total = 0

        for algo, data in results.items():
            tag = f"hl_{algo}"
            dups = data.get("duplicates_dict", {})
            if not isinstance(dups, dict):
                # fallback: top_phrases
                for item in data.get("top_phrases", []):
                    phrase = str(item[0] if isinstance(item, (list, tuple)) else item).strip()
                    if not phrase:
                        continue
                    self._highlight_phrase(tw, tag, full_text, phrase, covered)
                    total += 1
                continue

            for phrase, positions in dups.items():
                phrase = str(phrase).strip()
                if not phrase:
                    continue
                if not isinstance(positions, list):
                    positions = [positions] if isinstance(positions, (int, float)) else []

                for start in positions:
                    if not isinstance(start, (int, float)):
                        continue
                    start = int(start)
                    end = start + len(phrase)
                    if not (0 <= start < end <= len(full_text)):
                        continue
                    if (start, end) in covered:
                        continue
                    # Перевірка перекриття
                    if any(s < end and start < e for s, e in covered):
                        continue
                    try:
                        tw.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")
                        covered.add((start, end))
                        total += 1
                    except Exception:
                        pass

        print(f"[highlight] виділено {total} фрагментів")

    @staticmethod
    def _highlight_phrase(tw, tag, full_text, phrase, covered: set):
        lower = full_text.lower()
        start = 0
        while True:
            pos = lower.find(phrase.lower(), start)
            if pos == -1:
                break
            end = pos + len(phrase)
            key = (pos, end)
            if key not in covered:
                try:
                    tw.tag_add(tag, f"1.0+{pos}c", f"1.0+{end}c")
                    covered.add(key)
                except Exception:
                    pass
            start = pos + 1

    # ══════════════════════════════════════════════════════════════════════════
    # ДОПОМІЖНІ МЕТОДИ
    # ══════════════════════════════════════════════════════════════════════════

    def _display_text(self, formatted_text):
        tw = self.text_display
        tw.delete("1.0", tk.END)
        tw.tag_configure("bold",      font=("Courier", 10, "bold"))
        tw.tag_configure("italic",    font=("Courier", 10, "italic"))
        tw.tag_configure("underline", underline=True)

        if isinstance(formatted_text, list):
            pos = "1.0"
            for seg in formatted_text:
                text = seg.get("text", "")
                start = tw.index(pos)
                tw.insert(pos, text)
                end = tw.index(f"{pos}+{len(text)}c")
                fmt = seg.get("format", {})
                if fmt.get("bold"):      tw.tag_add("bold",      start, end)
                if fmt.get("italic"):    tw.tag_add("italic",    start, end)
                if fmt.get("underline"): tw.tag_add("underline", start, end)
                pos = end
        else:
            tw.insert("1.0", str(formatted_text or ""))

    def _update_file_info(self, stats: dict | None):
        if not stats:
            self.file_info_label.configure(text="📄 Файл не завантажено")
            return
        self.file_info_label.configure(
            text=(f"📊 {stats['char_count']} симв | "
                  f"📝 {stats['word_count']} слів | "
                  f"🎯 {stats['unique_words']} унік. | "
                  f"📏 {stats['avg_word_length']:.2f} сер.довж.")
        )

    def _set_ui_state(self, state: str):
        """Можна розширити для блокування кнопок під час аналізу."""
        pass

    def _on_table_right_click(self, event):
        """Контекстне меню: копіювати виділений рядок."""
        iid = self.result_table.identify_row(event.y)
        if not iid:
            return
        values = self.result_table.item(iid, "values")
        text = "\t".join(str(v) for v in values)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📋 Копіювати рядок",
                         command=lambda: self._copy_to_clipboard(text))
        menu.tk_popup(event.x_root, event.y_root)

    def _copy_to_clipboard(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    # ── Допоміжні будівельники ──────────────────────────────────────────────

    @staticmethod
    def _btn(parent, text, command, fg, hover, side="top", pady=6):
        btn = ctk.CTkButton(
            parent, text=text, command=command,
            font=("Helvetica", 11, "bold"), height=44,
            corner_radius=10, fg_color=fg, hover_color=hover,
            text_color="#0a0e27" if fg != "#ff006e" else "#ffffff",
        )
        btn.pack(fill="x", padx=14, pady=pady, side=side)
        return btn

    @staticmethod
    def _separator(parent):
        ctk.CTkFrame(parent, fg_color="#1a1f3a", height=2).pack(fill="x", padx=14, pady=10)

    # ══════════════════════════════════════════════════════════════════════════
    # FALLBACK (без customtkinter)
    # ══════════════════════════════════════════════════════════════════════════

    def _build_fallback_ui(self):
        """Мінімальний інтерфейс на чистому tkinter."""
        frm = tk.Frame(self.root, bg="#1a1a2e")
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Duplicate Finder", bg="#1a1a2e", fg="white",
                 font=("Arial", 18, "bold")).pack(pady=10)

        btn_frm = tk.Frame(frm, bg="#1a1a2e")
        btn_frm.pack(pady=5)

        for label, cmd in [
            ("Завантажити", self.load_file),
            ("Аналізувати", self.analyze),
            ("HTML",        self.open_html),
            ("JSON",        self.export_json),
            ("Txt звіт",   self.export_txt),
            ("Вийти",       self.logout),
        ]:
            tk.Button(btn_frm, text=label, command=cmd, width=14).pack(side="left", padx=4)

        # Алгоритм
        self.algorithm_var = tk.StringVar(value="All")
        for val in ["All", "Рабін-Карп", "Суфіксні дерева", "Семантичний",
                    "Нечіткий пошук", "N-грам аналіз"]:
            tk.Radiobutton(frm, text=val, variable=self.algorithm_var, value=val,
                           bg="#1a1a2e", fg="white", selectcolor="#333").pack(anchor="w", padx=20)

        ws_frm = tk.Frame(frm, bg="#1a1a2e")
        ws_frm.pack(anchor="w", padx=20)
        tk.Label(ws_frm, text="Довжина підрядка:", bg="#1a1a2e", fg="white").pack(side="left")
        self.window_size_entry = tk.Entry(ws_frm, width=6)
        self.window_size_entry.insert(0, "5")
        self.window_size_entry.pack(side="left", padx=5)

        self.file_info_label = tk.Label(frm, text="Файл не завантажено",
                                        bg="#1a1a2e", fg="#aaa")
        self.file_info_label.pack()

        # Таблиця
        cols = ("Алгоритм", "Дублікатів", "Унікальних", "Частота",
                "Час(с)", "Топ-фрази", "К-сть", "%")
        self.result_table = ttk.Treeview(frm, columns=cols, show="headings", height=4)
        for c in cols:
            self.result_table.heading(c, text=c)
            self.result_table.column(c, width=100)
        self.result_table.pack(fill="x", padx=10, pady=5)

        # Текст
        self.text_display = tk.Text(frm, wrap="word", font=("Courier", 10), height=20)
        self.text_display.pack(fill="both", expand=True, padx=10, pady=5)
