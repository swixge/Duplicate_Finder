
from datetime import datetime
import os


def generate_report(results, text_stats=None, file_path=None):
    """Create a readable TXT report for the user."""
    text_stats = text_stats or {}
    lines = [
        "=== ЗВІТ ПРО ПОШУК ПОВТОРІВ У ТЕКСТІ ===",
        f"Дата формування: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if file_path:
        lines.append(f"Файл: {os.path.basename(file_path)}")

    if text_stats:
        lines.extend([
            "",
            "Загальна характеристика документа:",
            f"- Символів: {text_stats.get('char_count', 0)}",
            f"- Слів: {text_stats.get('word_count', 0)}",
            f"- Унікальних слів: {text_stats.get('unique_words', 0)}",
            f"- Речень: {text_stats.get('sentence_count', 0)}",
            f"- Абзаців: {text_stats.get('paragraph_count', 0)}",
            f"- Середня довжина слова: {text_stats.get('avg_word_length', 0)}",
        ])

    lines.append("")
    lines.append("Пояснення показників:")
    lines.append("- Duplicates: кількість різних фрагментів, які повторюються.")
    lines.append("- Count: загальна кількість входжень повторюваних фрагментів.")
    lines.append("- Frequency: кількість повторних входжень без першого оригінального входження.")
    lines.append("- Percentage: частка тексту, покрита повторюваними фрагментами.")

    for algo, data in results.items():
        lines.extend([
            "",
            f"--- {algo} ---",
            f"Duplicates: {data.get('duplicates', 0)}",
            f"Unique words: {data.get('unique_count', 0)}",
            f"Frequency: {data.get('frequency', 0)}",
            f"Count: {data.get('count', 0)}",
            f"Percentage: {data.get('repeat_percentage', 0)}%",
            f"Quality: {data.get('quality_label', '')}",
            f"Recommendation: {data.get('recommendation', '')}",
            f"Processing time: {data.get('time', 0)} sec",
            "Top phrases:",
        ])

        for phrase, count in data.get("top_phrases", [])[:15]:
            lines.append(f" - {phrase} ({count})")

    return "\n".join(lines)
