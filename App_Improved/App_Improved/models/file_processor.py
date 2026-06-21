import os
import PyPDF2
import docx
from nltk.tokenize import word_tokenize
import traceback


class FileProcessor:
    """Модель для обробки PDF та DOCX файлів з покращеною стабільністю"""

    def __init__(self):
        self.supported_formats = [".pdf", ".docx"]

    def load_file(self, file_path: str) -> str:
        """Валідація та завантаження файлу"""
        if not file_path:
            raise ValueError("Шлях до файлу не вказано")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не знайдено: {file_path}")
        if not any(file_path.lower().endswith(fmt) for fmt in self.supported_formats):
            raise ValueError("Підтримуються лише файли формату PDF та DOCX")
        return file_path

    def extract_text(self, file_path: str):
        """Витягнення тексту з підтримкою помилок"""
        try:
            if file_path.lower().endswith(".pdf"):
                return self._extract_from_pdf(file_path)
            elif file_path.lower().endswith(".docx"):
                return self._extract_from_docx(file_path)
        except Exception as e:
            print(f"Помилка витягнення тексту: {str(e)}")
            traceback.print_exc()
            raise RuntimeError(f"Не вдалося витягнути текст з файлу: {str(e)}")
        return []

    def _extract_from_pdf(self, file_path):
        """Витягнення тексту з PDF"""
        formatted_text = []
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    extracted = page.extract_text()
                    if extracted and extracted.strip():
                        lines = extracted.split('\n')
                        for line in lines:
                            if line.strip():
                                formatted_text.append({"text": line + "\n", "format": {}})
            return formatted_text if formatted_text else [{"text": "Текст відсутній у PDF", "format": {}}]
        except Exception as e:
            raise RuntimeError(f"Помилка читання PDF: {str(e)}")

    def _extract_from_docx(self, file_path):
        """Витягнення тексту з DOCX з форматуванням"""
        formatted_text = []
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    for run in para.runs:
                        if run.text.strip():
                            run_format = {
                                "bold": bool(run.bold),
                                "italic": bool(run.italic),
                                "underline": bool(run.underline),
                            }
                            if run.font.size:
                                run_format["size"] = run.font.size.pt
                            if run.font.name:
                                run_format["font"] = run.font.name
                            formatted_text.append({"text": run.text, "format": run_format})
                    formatted_text.append({"text": "\n", "format": {}})
            return formatted_text if formatted_text else [{"text": "Текст відсутній у DOCX", "format": {}}]
        except Exception as e:
            raise RuntimeError(f"Помилка читання DOCX: {str(e)}")

    def analyze_text(self, text_data):
        """Аналіз тексту з покращеною обробкою помилок"""
        if not text_data:
            return self._empty_stats()

        # Якщо текст у форматі списку сегментів
        if isinstance(text_data, list):
            flat_text = "".join(segment.get("text", "") for segment in text_data)
        else:
            flat_text = str(text_data)

        if not flat_text or flat_text.strip() == "Текст відсутній":
            return self._empty_stats()

        try:
            words = word_tokenize(flat_text)
            words = [w for w in words if w.isalnum()]

            char_count = len(flat_text)
            word_count = len(words)
            unique_words = len(set(words))
            avg_word_length = round(sum(len(w) for w in words) / word_count, 2) if word_count > 0 else 0.0
            longest_word = max(words, key=len, default="")
            shortest_word = min(words, key=len, default="") if words else ""

            return {
                "char_count": char_count,
                "word_count": word_count,
                "unique_words": unique_words,
                "avg_word_length": avg_word_length,
                "longest_word": longest_word,
                "shortest_word": shortest_word,
            }
        except Exception as e:
            print(f"Помилка аналізу тексту: {e}")
            return self._empty_stats()

    @staticmethod
    def _empty_stats():
        return {
            "char_count": 0,
            "word_count": 0,
            "unique_words": 0,
            "avg_word_length": 0.0,
            "longest_word": "",
            "shortest_word": "",
        }