import os
import webbrowser
from models import FileProcessor, AlgorithmComparator, DatabaseManager


class MainController:
    """Main controller for application logic"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.comparator = AlgorithmComparator()
        self.db = DatabaseManager()
        self.user = None
        self.is_admin = False
        self.file_path = None
        self.file_id = None
        self.file_text = None
        self.file_results = None
        self.file_text_stats = None

    def login(self, role, password=None):
        """Handle user login"""
        if role == "Адміністратор" and password != "admin123":
            raise ValueError("Невірний пароль")
        self.user = "admin" if role == "Адміністратор" else "guest"
        self.is_admin = role == "Адміністратор"
        return True

    def load_file(self, file_path):
        """Load and process file"""
        if not file_path or not os.path.exists(file_path):
            raise ValueError("Файл не знайдено")
            
        print(f"Контролер: виклик load_file з шляхом {file_path}")
        self.file_path = self.file_processor.load_file(file_path)
        self.file_text = self.file_processor.extract_text(self.file_path)
        self.file_text_stats = self.file_processor.analyze_text(self.file_text)
        print(f"Контролер: збереження файлу в базу даних")
        self.file_id = self.db.save_file(self.file_path, self.user, self.file_text_stats)
        self.file_results = None
        return True

    def set_window_size(self, size):
        """Set window size for algorithms"""
        try:
            self.comparator.suffix_tree.set_window_size(size)
            self.comparator.rabin_karp.window_size = size
        except ValueError:
            raise ValueError("Некоректна довжина підрядка")

    def analyze(self, algorithm=None):
        if not self.file_path:
            raise ValueError("Файл не завантажено")
        
        text = "".join(t["text"] for t in self.file_text) if isinstance(self.file_text, list) else self.file_text
        
        if algorithm:
            result = self.comparator.analyze_single_algorithm(text, algorithm)
        else:
            result = self.comparator.compare_algorithms(text)
        
        self.db.save_results(self.file_id, result)
        self.file_results = result
        return result   # ←←← повинен повертати dict

    def generate_highlighted_html(self, text, results, window_size):
        """Generate HTML file with highlighted duplicates"""
        print("Генерація HTML-файлу з підсвіткою")
        if not text.strip() or not results:
            print("Текст або результати порожні, HTML не генерується")
            return None
        
        highlighted = []
        char_pos = 0
        highlighted_phrases = set()
        colors = {
            "Рабін-Карп": "#FF6B6B",
            "Суфіксні дерева": "#4ECDC4",
            "Семантичний": "#45B7D1",
            "Нечіткий пошук": "#FFD93D",
            "N-грам аналіз": "#A8E6CF"
        }

        for algo, data in results.items():
            for phrase, _ in data["top_phrases"]:
                positions = []
                start_pos = 0
                while True:
                    pos = text.lower().find(phrase.lower(), start_pos)
                    if pos == -1:
                        break
                    positions.append((pos, pos + len(phrase)))
                    start_pos = pos + 1
                
                for start, end in positions:
                    if (phrase, start) not in highlighted_phrases:
                        if char_pos < start:
                            highlighted.append(
                                text[char_pos:start].replace("\n", "<br>")
                                .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            )
                        highlighted.append(
                            f'<span style="background-color: {colors[algo]}">'
                            f'{text[start:end].replace("\n", "<br>").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}'
                            f'</span>'
                        )
                        char_pos = end
                        highlighted_phrases.add((phrase, start))

        if char_pos < len(text):
            highlighted.append(
                text[char_pos:].replace("\n", "<br>")
                .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Highlighted Text</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; white-space: pre-wrap; line-height: 1.5; }}
        span {{ padding: 2px; }}
    </style>
</head>
<body>
    {''.join(highlighted)}
</body>
</html>"""
        
        file_name = f"highlighted_{self.file_id}.html"
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML-файл створено: {file_name}")
            return file_name
        except Exception as e:
            print(f"Помилка при збереженні HTML: {str(e)}")
            return None

    def open_highlighted_file(self, highlighted_file):
        """Open highlighted HTML file in browser"""
        if highlighted_file and os.path.exists(highlighted_file):
            webbrowser.open(f"file://{os.path.abspath(highlighted_file)}")
        else:
            raise FileNotFoundError("Файл із підсвіткою не знайдено")

    def get_highlighted_html_path(self):
        """Get path to highlighted HTML file"""
        file_info = self.db.get_file_info(self.file_id)
        if file_info and file_info["highlighted_file"]:
            return file_info["highlighted_file"]
        return None

    def get_statistics(self):
        """Get statistics for current file"""
        if not self.file_id:
            raise ValueError("Файл не завантажено")
        return self.db.get_stats(self.file_id)

    def get_all_files(self):
        """Get all files (admin only)"""
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        return self.db.get_all_files()

    def get_file_stats(self, file_id):
        """Get statistics for specific file (admin only)"""
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        return self.db.get_file_stats(file_id)

    def get_file_info(self, file_id):
        """Get file information (admin only)"""
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        return self.db.get_file_info(file_id)

    def delete_file(self, file_id):
        """Delete file (admin only)"""
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        self.db.delete_file(file_id)

    def cleanup(self):
        """Cleanup resources"""
        self.db.close()
