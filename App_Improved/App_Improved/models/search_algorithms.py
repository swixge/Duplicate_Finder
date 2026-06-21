import hashlib
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import wordnet, stopwords
from collections import Counter
import math
import re
from difflib import SequenceMatcher


def _find_all_positions(text: str, phrase: str) -> list:
    """Знаходить усі позиції входження фрази в тексті (регістронезалежно)."""
    positions = []
    lower_text = text.lower()
    lower_phrase = phrase.lower()
    start = 0
    while True:
        pos = lower_text.find(lower_phrase, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


class RabinKarpSearch:
    """Rabin-Karp із великим простим модулем — мінімальні колізії."""

    BASE = 257
    MOD = (1 << 61) - 1  # Mersenne prime

    def __init__(self, window_size=5):
        self.window_size = max(4, int(window_size))

    def _rolling_hash(self, text: str):
        """Генератор (хеш, позиція) для всіх вікон довжиною window_size."""
        n = self.window_size
        if len(text) < n:
            return
        base_n = pow(self.BASE, n - 1, self.MOD)
        h = 0
        for ch in text[:n]:
            h = (h * self.BASE + ord(ch)) % self.MOD
        yield h, 0
        for i in range(1, len(text) - n + 1):
            h = (h - ord(text[i - 1]) * base_n) % self.MOD
            h = (h * self.BASE + ord(text[i + n - 1])) % self.MOD
            yield h, i

    def find_duplicates(self, text: str):
        if not text or len(text) < self.window_size:
            return {}, []

        hash_map: dict[int, list[int]] = {}
        duplicates: dict[str, list[int]] = {}

        for h, i in self._rolling_hash(text):
            if h in hash_map:
                candidate = text[i:i + self.window_size]
                for prev_i in hash_map[h]:
                    if text[prev_i:prev_i + self.window_size] == candidate:
                        if candidate not in duplicates:
                            duplicates[candidate] = []
                        for pos in (prev_i, i):
                            if pos not in duplicates[candidate]:
                                duplicates[candidate].append(pos)
                hash_map[h].append(i)
            else:
                hash_map[h] = [i]

        # Залишаємо фрази ≥ window_size символів (пробіли та знаки не рахуємо як "змістовні")
        duplicates = {
            k: sorted(v)
            for k, v in duplicates.items()
            if len(k.strip()) >= self.window_size and not k.strip().isspace()
        }
        return duplicates, []


class SuffixTreeSearch:
    """LCP по відсортованих суфіксах — знаходить найдовші повторювані підрядки."""

    def __init__(self, window_size=8):
        self.window_size = max(6, int(window_size))

    def set_window_size(self, size: int):
        self.window_size = max(6, int(size))

    def find_duplicates(self, text: str):
        if not text or len(text) < self.window_size:
            return {}, []

        suffixes = sorted((text[i:], i) for i in range(len(text)))
        duplicates: dict[str, list[int]] = {}

        for i in range(len(suffixes) - 1):
            suffix1, pos1 = suffixes[i]
            suffix2, pos2 = suffixes[i + 1]

            lcp = 0
            min_len = min(len(suffix1), len(suffix2))
            while lcp < min_len and suffix1[lcp] == suffix2[lcp]:
                lcp += 1

            if lcp >= self.window_size:
                repeated = suffix1[:lcp]
                # Не беремо суто пробільні фрази
                if not repeated.strip() or len(repeated.strip()) < self.window_size:
                    continue

                # Нормалізуємо: обрізаємо пробіли з країв один раз
                repeated = repeated.strip()

                # Позиції у вихідному тексті
                positions = _find_all_positions(text, repeated)
                if len(positions) >= 2:
                    duplicates[repeated] = positions

        return duplicates, []


class SemanticSearch:
    """Семантичний пошук: повторювані n-грами (2-4 слова) + синонімічні групи."""

    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def find_duplicates(self, text: str):
        if not text:
            return {}, []

        try:
            tokens = word_tokenize(text.lower())
        except Exception:
            tokens = re.findall(r"[a-zA-ZЀ-ӿ]+", text.lower())
        clean_tokens = [w for w in tokens if w.isalnum() and w not in self.stop_words]

        if len(clean_tokens) < 3:
            return {}, []

        duplicates: dict[str, list] = {}

        # 1. Повторювані n-грами (2–4 слова)
        for n in range(2, 5):
            ngram_positions: dict[str, list[int]] = {}
            for i in range(len(clean_tokens) - n + 1):
                phrase = ' '.join(clean_tokens[i:i + n])
                positions = _find_all_positions(text, phrase)
                if len(positions) >= 2:
                    ngram_positions[phrase] = positions
            duplicates.update(ngram_positions)

        # 2. Синонімічні групи — слова, що мають спільну лему WordNet
        try:
            from collections import defaultdict
            lemma_to_words: dict = defaultdict(set)
            for token in set(clean_tokens):
                synsets = wordnet.synsets(token)
                if synsets:
                    lemma = synsets[0].lemmas()[0].name()
                    lemma_to_words[lemma].add(token)
            for lemma, word_set in lemma_to_words.items():
                if len(word_set) > 1:
                    key = f"синоніми: {lemma} ({', '.join(sorted(word_set))})"
                    duplicates[key] = list(word_set)
        except Exception:
            pass  # WordNet недоступний — пропускаємо синонімічний аналіз

        return duplicates, []


class FuzzyMatchSearch:
    """Fuzzy Matching — порівнює речення/рядки між собою."""

    def __init__(self, threshold=0.82):
        self.threshold = threshold

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def find_duplicates(self, text: str):
        if not text:
            return {}, []

        # Ділимо на речення (враховуємо і рядковий розбій)
        raw_lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        if len(raw_lines) < 2:
            return {}, []

        duplicates: dict[str, list[int]] = {}

        for i in range(len(raw_lines)):
            for j in range(i + 1, len(raw_lines)):
                sim = self._similarity(raw_lines[i], raw_lines[j])
                if sim >= self.threshold:
                    key = raw_lines[i]
                    if key not in duplicates:
                        duplicates[key] = _find_all_positions(text, raw_lines[i])
                    # Додаємо позиції другого рядка
                    for pos in _find_all_positions(text, raw_lines[j]):
                        if pos not in duplicates[key]:
                            duplicates[key].append(pos)

        for k in duplicates:
            duplicates[k] = sorted(duplicates[k])

        return duplicates, []


class NGramAnalysis:
    """N-gram аналіз — підраховує повторювані послідовності слів."""

    def __init__(self, n=3):
        self.n = n
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def _tokenize(self, text: str) -> list:
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = re.findall(r"[a-zA-ZЀ-ӿ]+", text)
        return [w.lower() for w in tokens
                if w.lower() not in self.stop_words and w.isalnum()]

    def find_duplicates(self, text: str):
        if not text:
            return {}, []

        tokens = self._tokenize(text)
        if len(tokens) < 2:
            return {}, []

        duplicates: dict[str, list[int]] = {}

        for n in range(2, min(6, len(tokens))):
            counts: Counter = Counter()
            for i in range(len(tokens) - n + 1):
                counts[' '.join(tokens[i:i + n])] += 1

            for phrase, count in counts.items():
                if count >= 2:
                    positions = _find_all_positions(text, phrase)
                    if len(positions) >= 2 and phrase not in duplicates:
                        duplicates[phrase] = positions

        return duplicates, []


class DocumentationAnalysis:
    """Аналіз документації: повторювані параграфи та патерни."""

    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def find_duplicates(self, text: str):
        if not text:
            return {}, []

        paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
        duplicates: dict[str, list[int]] = {}

        # Порівнюємо параграфи
        for i in range(len(paragraphs)):
            for j in range(i + 1, len(paragraphs)):
                ratio = SequenceMatcher(None, paragraphs[i].lower(), paragraphs[j].lower()).ratio()
                if ratio >= 0.65:
                    key = paragraphs[i][:80] + ("..." if len(paragraphs[i]) > 80 else "")
                    if key not in duplicates:
                        duplicates[key] = _find_all_positions(text, paragraphs[i][:40])
                    for pos in _find_all_positions(text, paragraphs[j][:40]):
                        if pos not in duplicates[key]:
                            duplicates[key].append(pos)

        # Повторювані слова всередині секцій
        tokens = [w.lower() for w in word_tokenize(text)
                  if w.isalnum() and w.lower() not in self.stop_words]
        word_counts = Counter(tokens)
        for word, count in word_counts.items():
            if count >= 4 and len(word) > 4:
                positions = _find_all_positions(text, word)
                key = f"часте слово: {word} (×{count})"
                duplicates[key] = positions

        return duplicates, []
