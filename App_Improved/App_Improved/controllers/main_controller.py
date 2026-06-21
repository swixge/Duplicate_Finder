import os
import json
import webbrowser
from datetime import datetime
from models import FileProcessor, AlgorithmComparator, DatabaseManager


class MainController:
    """Головний контролер додатку."""

    def __init__(self):
        self.file_processor = FileProcessor()
        self.comparator = AlgorithmComparator()
        self.db = DatabaseManager()
        self.user: str | None = None
        self.is_admin: bool = False
        self.file_path: str | None = None
        self.file_id: int | None = None
        self.file_text = None          # list[dict] | str
        self.file_results: dict | None = None
        self.file_text_stats: dict | None = None

    # ─── авторизація ─────────────────────────────────────────────────────────

    def login(self, role: str, password: str | None = None) -> bool:
        if role == "Адміністратор" and password != "admin123":
            raise ValueError("Невірний пароль")
        self.user = "admin" if role == "Адміністратор" else "guest"
        self.is_admin = role == "Адміністратор"
        return True

    # ─── файли ───────────────────────────────────────────────────────────────

    def load_file(self, file_path: str) -> bool:
        if not file_path or not os.path.exists(file_path):
            raise ValueError("Файл не знайдено")
        self.file_path = self.file_processor.load_file(file_path)
        self.file_text = self.file_processor.extract_text(self.file_path)
        self.file_text_stats = self.file_processor.analyze_text(self.file_text)
        self.file_id = self.db.save_file(self.file_path, self.user, self.file_text_stats)
        self.file_results = None
        return True

    def set_window_size(self, size: int):
        try:
            size = int(size)
            self.comparator.suffix_tree.set_window_size(size)
            self.comparator.rabin_karp.window_size = max(4, size)
        except (TypeError, ValueError):
            raise ValueError("Некоректна довжина підрядка")

    def get_plain_text(self) -> str:
        """Повертає суцільний текст незалежно від формату file_text."""
        if isinstance(self.file_text, list):
            return "".join(seg.get("text", "") for seg in self.file_text)
        return str(self.file_text or "")

    # ─── аналіз ──────────────────────────────────────────────────────────────

    def analyze(self, algorithm: str | None = None) -> dict:
        if not self.file_path:
            raise ValueError("Файл не завантажено")

        text = self.get_plain_text()

        if algorithm:
            result = self.comparator.analyze_single_algorithm(text, algorithm)
        else:
            result = self.comparator.compare_algorithms(text)

        self.db.save_results(self.file_id, result)
        self.file_results = result
        return result

    # ─── підсвітка HTML ──────────────────────────────────────────────────────

    def generate_highlighted_html(self, text: str, results: dict, window_size: int) -> str | None:
        if not text.strip() or not results:
            return None

        colors = {
            "Рабін-Карп":      "#FF6B6B",
            "Суфіксні дерева": "#4ECDC4",
            "Семантичний":     "#45B7D1",
            "Нечіткий пошук":  "#FFD93D",
            "N-грам аналіз":   "#A8E6CF",
        }

        # Збираємо всі (start, end, color) та сортуємо за позицією
        spans: list[tuple[int, int, str]] = []
        for algo, data in results.items():
            color = colors.get(algo, "#cccccc")
            dups = data.get("duplicates_dict", data.get("duplicates", {}))
            if not isinstance(dups, dict):
                continue
            for phrase, positions in dups.items():
                phrase = str(phrase)
                if not isinstance(positions, list):
                    positions = [positions] if isinstance(positions, (int, float)) else []
                for start in positions:
                    if not isinstance(start, (int, float)):
                        continue
                    start = int(start)
                    end = start + len(phrase)
                    if 0 <= start < end <= len(text):
                        spans.append((start, end, color))

        # Сортуємо за початком, при рівності — більш довгі першими
        spans.sort(key=lambda x: (x[0], -x[1]))

        # Формуємо HTML без перекриттів
        html_parts = []
        cursor = 0

        def esc(s: str) -> str:
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        for start, end, color in spans:
            if start < cursor:
                continue
            if cursor < start:
                html_parts.append(esc(text[cursor:start]))
            html_parts.append(
                f'<span style="background:{color};padding:1px 2px;border-radius:2px">'
                f'{esc(text[start:end])}</span>'
            )
            cursor = end

        if cursor < len(text):
            html_parts.append(esc(text[cursor:]))

        # Легенда
        legend_items = "".join(
            f'<span style="background:{c};padding:2px 8px;border-radius:4px;margin:2px">{a}</span>'
            for a, c in colors.items() if a in results
        )

        html_content = f"""<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <title>Підсвічені дублікати</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px;
            background:#1a1a2e; color:#e0e0e0; line-height:1.7; }}
    .legend {{ margin-bottom:20px; padding:10px; background:#0f1535;
               border-radius:8px; }}
    .content {{ background:#0f1535; padding:20px; border-radius:8px;
                white-space:pre-wrap; font-family:Consolas,monospace; font-size:13px; }}
    h2 {{ color:#00d4ff; }}
  </style>
</head>
<body>
  <h2>🔍 Результати пошуку дублікатів</h2>
  <div class="legend"><strong>Легенда:</strong> {legend_items}</div>
  <div class="content">{''.join(html_parts)}</div>
</body>
</html>"""

        file_name = f"highlighted_{self.file_id}.html"
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(html_content)
            return file_name
        except Exception as e:
            print(f"Помилка збереження HTML: {e}")
            return None

    def open_highlighted_file(self, highlighted_file: str):
        if highlighted_file and os.path.exists(highlighted_file):
            webbrowser.open(f"file://{os.path.abspath(highlighted_file)}")
        else:
            raise FileNotFoundError("Файл із підсвіткою не знайдено")

    # ─── експорт ─────────────────────────────────────────────────────────────

    def export_results_json(self, output_path: str | None = None) -> str:
        """Зберігає results у JSON-файл, повертає шлях."""
        if not self.file_results:
            raise ValueError("Немає результатів для експорту. Спочатку запустіть аналіз.")
        if not output_path:
            output_path = f"results_{self.file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {}
        for algo, data in self.file_results.items():
            export_data[algo] = {
                "duplicates": data.get("duplicates", 0),
                "unique_count": data.get("unique_count", 0),
                "frequency": data.get("frequency", 0),
                "time": data.get("time", 0),
                "repeat_percentage": data.get("repeat_percentage", 0),
                "top_phrases": data.get("top_phrases", []),
            }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        return output_path

    def export_results_txt(self, output_path: str | None = None) -> str:
        """Зберігає results у текстовий звіт, повертає шлях."""
        if not self.file_results:
            raise ValueError("Немає результатів для експорту.")
        if not output_path:
            output_path = f"report_{self.file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        lines = [
            "=" * 60,
            "  ЗВІТ АНАЛІЗУ ДУБЛІКАТІВ",
            f"  Файл: {self.file_path}",
            f"  Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
        ]
        for algo, data in self.file_results.items():
            lines += [
                f"▶ {algo}",
                f"   Дублікатів:      {data.get('duplicates', 0)}",
                f"   Унікальних:      {data.get('unique_count', 0)}",
                f"   Частота:         {data.get('frequency', 0)}",
                f"   % покриття:      {data.get('repeat_percentage', 0):.2f}%",
                f"   Час (с):         {data.get('time', 0):.4f}",
                "   Топ фрази:",
            ]
            for phrase, cnt in data.get("top_phrases", [])[:10]:
                lines.append(f"     • {phrase!r}  ×{cnt}")
            lines.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output_path

    # ─── статистика / БД ─────────────────────────────────────────────────────

    def get_statistics(self) -> dict | None:
        if not self.file_id:
            raise ValueError("Файл не завантажено")
        return self.db.get_stats(self.file_id)

    def get_all_files(self):
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        return self.db.get_all_files()

    def get_file_stats(self, file_id: int):
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        return self.db.get_file_stats(file_id)

    def get_file_info(self, file_id: int):
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        return self.db.get_file_info(file_id)

    def delete_file(self, file_id: int):
        if not self.is_admin:
            raise ValueError("Доступ лише для адміністратора")
        self.db.delete_file(file_id)

    def cleanup(self):
        self.db.close()
