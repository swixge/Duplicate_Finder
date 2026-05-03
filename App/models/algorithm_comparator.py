import time
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from .search_algorithms import (
    RabinKarpSearch, SuffixTreeSearch, SemanticSearch,
    FuzzyMatchSearch, NGramAnalysis
)


class AlgorithmComparator:
    """Виправлений координатор з правильним підрахунком дублікатів і відсотка"""

    def __init__(self):
        self.rabin_karp = RabinKarpSearch()
        self.suffix_tree = SuffixTreeSearch()
        self.semantic = SemanticSearch()
        self.fuzzy_match = FuzzyMatchSearch()
        self.ngram = NGramAnalysis()

    def compare_algorithms(self, text: str) -> dict:
        results = {}
        results["Рабін-Карп"] = self._run_rabin_karp(text)
        results["Суфіксні дерева"] = self._run_suffix_tree(text)
        results["Семантичний"] = self._run_semantic(text)
        results["Нечіткий пошук"] = self._run_fuzzy_match(text)
        results["N-грам аналіз"] = self._run_ngram(text)
        return results

    def analyze_single_algorithm(self, text: str, algorithm: str) -> dict:
        if algorithm == "Рабін-Карп":
            return {"Рабін-Карп": self._run_rabin_karp(text)}
        elif algorithm == "Суфіксні дерева":
            return {"Суфіксні дерева": self._run_suffix_tree(text)}
        elif algorithm == "Семантичний":
            return {"Семантичний": self._run_semantic(text)}
        elif algorithm == "Нечіткий пошук":
            return {"Нечіткий пошук": self._run_fuzzy_match(text)}
        elif algorithm == "N-грам аналіз":
            return {"N-грам аналіз": self._run_ngram(text)}
        else:
            raise ValueError(f"Невідомий алгоритм: {algorithm}")

        # ====================== ВИПРАВЛЕНА ЛОГІКА ======================
    def _calculate_coverage_percentage(self, text: str, duplicates: dict) -> float:
        """Правильний розрахунок % покриття"""
        if not text or not duplicates:
            return 0.0
        
        covered = set()
        for phrase, positions in duplicates.items():
            if not isinstance(positions, list):
                positions = [positions] if isinstance(positions, (int, float)) else []
            for start in positions:
                if not isinstance(start, (int, float)):
                    continue
                start = int(start)
                end = min(start + len(phrase), len(text))
                for i in range(start, end):
                    covered.add(i)
        
        return round((len(covered) / len(text)) * 100, 2)

        # ====================== ВИПРАВЛЕНА ЛОГІКА ======================
    def _calculate_coverage_percentage(self, text: str, duplicates: dict) -> float:
        if not text or not duplicates:
            return 0.0
        covered = set()
        for phrase, positions in duplicates.items():
            if not isinstance(positions, list):
                positions = [positions] if isinstance(positions, (int, float)) else []
            for start in positions:
                if not isinstance(start, (int, float)):
                    continue
                start = int(start)
                end = min(start + len(phrase), len(text))
                for i in range(start, end):
                    covered.add(i)
        return round((len(covered) / len(text)) * 100, 2)

    # ====================== ВИПРАВЛЕНІ МЕТОДИ ======================
    def _run_rabin_karp(self, text: str):
        start = time.time()
        duplicates, positions = self.rabin_karp.find_duplicates(text)
        percentage = self._calculate_coverage_percentage(text, duplicates)
        freq = Counter({k: len(v) for k, v in duplicates.items() if v})

        # Правильний Unique — кількість слів, які зустрічаються рівно 1 раз
        word_counts = Counter(text.split())
        unique_count = sum(1 for count in word_counts.values() if count == 1)

        return {
            "duplicates": len(duplicates),
            "unique_count": unique_count,
            "frequency": sum(len(v) for v in duplicates.values()),
            "time": round(time.time() - start, 4),
            "top_phrases": freq.most_common(30),
            "positions": positions,
            "repeat_percentage": percentage
        }

    def _run_suffix_tree(self, text: str):
        start = time.time()
        duplicates, positions = self.suffix_tree.find_duplicates(text)
        percentage = self._calculate_coverage_percentage(text, duplicates)
        freq = Counter({k: len(v) for k, v in duplicates.items() if v})

        word_counts = Counter(text.split())
        unique_count = sum(1 for count in word_counts.values() if count == 1)

        return {
            "duplicates": len(duplicates),
            "unique_count": unique_count,
            "frequency": sum(len(v) for v in duplicates.values()),
            "time": round(time.time() - start, 4),
            "top_phrases": freq.most_common(30),
            "positions": positions,
            "repeat_percentage": percentage
        }

    def _run_semantic(self, text: str):
        start = time.time()
        duplicates, positions = self.semantic.find_duplicates(text)
        percentage = self._calculate_coverage_percentage(text, duplicates)
        freq = Counter({k: len(v) if isinstance(v, list) else 1 for k, v in duplicates.items()})

        word_counts = Counter(text.split())
        unique_count = sum(1 for count in word_counts.values() if count == 1)

        return {
            "duplicates": len(duplicates),
            "unique_count": unique_count,
            "frequency": sum(len(v) if isinstance(v, list) else 1 for v in duplicates.values()),
            "time": round(time.time() - start, 4),
            "top_phrases": freq.most_common(30),
            "positions": positions,
            "repeat_percentage": percentage
        }

    def _run_fuzzy_match(self, text: str):
        start = time.time()
        duplicates, positions = self.fuzzy_match.find_duplicates(text)
        percentage = self._calculate_coverage_percentage(text, duplicates)
        freq = Counter({k: len(v) for k, v in duplicates.items() if v})

        word_counts = Counter(text.split())
        unique_count = sum(1 for count in word_counts.values() if count == 1)

        return {
            "duplicates": len(duplicates),
            "unique_count": unique_count,
            "frequency": sum(len(v) for v in duplicates.values()),
            "time": round(time.time() - start, 4),
            "top_phrases": freq.most_common(30),
            "positions": positions,
            "repeat_percentage": percentage
        }

    def _run_ngram(self, text: str):
        start = time.time()
        duplicates, positions = self.ngram.find_duplicates(text)
        percentage = self._calculate_coverage_percentage(text, duplicates)
        freq = Counter({k: len(v) for k, v in duplicates.items() if v})

        word_counts = Counter(text.split())
        unique_count = sum(1 for count in word_counts.values() if count == 1)

        return {
            "duplicates": len(duplicates),
            "unique_count": unique_count,
            "frequency": sum(len(v) for v in duplicates.values()),
            "time": round(time.time() - start, 4),
            "top_phrases": freq.most_common(30),
            "positions": positions,
            "repeat_percentage": percentage
        }