import time
from collections import Counter
from .search_algorithms import (
    RabinKarpSearch, SuffixTreeSearch, SemanticSearch,
    FuzzyMatchSearch, NGramAnalysis
)


class AlgorithmComparator:
    """Координатор алгоритмів пошуку дублікатів."""

    def __init__(self):
        self.rabin_karp = RabinKarpSearch()
        self.suffix_tree = SuffixTreeSearch()
        self.semantic = SemanticSearch()
        self.fuzzy_match = FuzzyMatchSearch()
        self.ngram = NGramAnalysis()

    # ─── публічний API ───────────────────────────────────────────────────────

    def compare_algorithms(self, text: str) -> dict:
        results = {}
        for name, runner in self._all_runners():
            results[name] = runner(text)
        return results

    def analyze_single_algorithm(self, text: str, algorithm: str) -> dict:
        runners = dict(self._all_runners())
        if algorithm not in runners:
            raise ValueError(f"Невідомий алгоритм: {algorithm}")
        return {algorithm: runners[algorithm](text)}

    def _all_runners(self):
        return [
            ("Рабін-Карп",      self._run_rabin_karp),
            ("Суфіксні дерева", self._run_suffix_tree),
            ("Семантичний",     self._run_semantic),
            ("Нечіткий пошук",  self._run_fuzzy_match),
            ("N-грам аналіз",   self._run_ngram),
        ]

    # ─── внутрішні методи ────────────────────────────────────────────────────

    @staticmethod
    def _calculate_coverage_percentage(text: str, duplicates: dict) -> float:
        """Частка символів тексту, що входять у знайдені дублікати."""
        if not text or not duplicates:
            return 0.0
        covered: set[int] = set()
        for phrase, positions in duplicates.items():
            if not isinstance(positions, list):
                positions = [positions] if isinstance(positions, (int, float)) else []
            phrase_len = len(str(phrase))
            for start in positions:
                if not isinstance(start, (int, float)):
                    continue
                start = int(start)
                end = min(start + phrase_len, len(text))
                covered.update(range(start, end))
        return round(len(covered) / len(text) * 100, 2)

    @staticmethod
    def _unique_word_count(text: str) -> int:
        word_counts = Counter(text.lower().split())
        return sum(1 for c in word_counts.values() if c == 1)

    @staticmethod
    def _build_result(text: str, duplicates: dict, positions: list, elapsed: float) -> dict:
        unique_count = AlgorithmComparator._unique_word_count(text)
        percentage = AlgorithmComparator._calculate_coverage_percentage(text, duplicates)

        # top_phrases: для кожної фрази — кількість входжень
        freq: Counter = Counter()
        for phrase, pos_list in duplicates.items():
            if isinstance(pos_list, list):
                freq[phrase] = len(pos_list)
            elif isinstance(pos_list, (int, float)):
                freq[phrase] = 1

        return {
            "duplicates": len(duplicates),
            "unique_count": unique_count,
            "frequency": sum(freq.values()),
            "time": round(elapsed, 4),
            "top_phrases": freq.most_common(30),
            "duplicates_dict": duplicates,   # для підсвітки
            "positions": positions,
            "repeat_percentage": percentage,
        }

    def _run_rabin_karp(self, text: str) -> dict:
        t = time.time()
        dups, pos = self.rabin_karp.find_duplicates(text)
        return self._build_result(text, dups, pos, time.time() - t)

    def _run_suffix_tree(self, text: str) -> dict:
        t = time.time()
        dups, pos = self.suffix_tree.find_duplicates(text)
        return self._build_result(text, dups, pos, time.time() - t)

    def _run_semantic(self, text: str) -> dict:
        t = time.time()
        dups, pos = self.semantic.find_duplicates(text)
        return self._build_result(text, dups, pos, time.time() - t)

    def _run_fuzzy_match(self, text: str) -> dict:
        t = time.time()
        dups, pos = self.fuzzy_match.find_duplicates(text)
        return self._build_result(text, dups, pos, time.time() - t)

    def _run_ngram(self, text: str) -> dict:
        t = time.time()
        dups, pos = self.ngram.find_duplicates(text)
        return self._build_result(text, dups, pos, time.time() - t)
