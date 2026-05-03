import hashlib
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet, stopwords
from collections import Counter
import math
from difflib import SequenceMatcher


class RabinKarpSearch:
    """Rabin-Karp — виправлений для реальних дублікатів"""

    def __init__(self, window_size=10):
        self.window_size = max(8, int(window_size))

    def _hash(self, text):
        h = 0
        for char in text:
            h = (h * 256 + ord(char)) % 101
        return h

    def find_duplicates(self, text):
        if not text or len(text) < self.window_size:
            return {}, []

        duplicates = {}
        hash_dict = {}

        for i in range(len(text) - self.window_size + 1):
            substring = text[i:i + self.window_size]
            h = self._hash(substring)

            if h in hash_dict:
                for prev_i in hash_dict[h]:
                    if text[prev_i:prev_i + self.window_size] == substring:
                        if substring not in duplicates:
                            duplicates[substring] = []
                        if i not in duplicates[substring]:
                            duplicates[substring].append(i)
                        if prev_i not in duplicates[substring]:
                            duplicates[substring].append(prev_i)
            else:
                hash_dict[h] = [i]

        # Жорсткий фільтр — тільки достатньо довгі фрази
        duplicates = {k: v for k, v in duplicates.items() if len(k) >= 8 and len(k.split()) >= 1}

        return duplicates, []


class SuffixTreeSearch:
    """Suffix Tree — виправлений для реальних дублікатів"""

    def __init__(self, window_size=10):
        self.window_size = max(10, int(window_size))

    def set_window_size(self, size):
        self.window_size = max(10, int(size))

    def find_duplicates(self, text):
        if not text or len(text) < self.window_size:
            return {}, []

        suffixes = sorted((text[i:], i) for i in range(len(text)))
        duplicates = {}

        for i in range(len(suffixes) - 1):
            suffix1, pos1 = suffixes[i]
            suffix2, pos2 = suffixes[i + 1]

            lcp = 0
            min_len = min(len(suffix1), len(suffix2))
            while lcp < min_len and suffix1[lcp] == suffix2[lcp]:
                lcp += 1

            if lcp >= self.window_size:
                repeated = suffix1[:lcp].strip()
                # Фільтруємо короткі та загальні фрази
                if len(repeated) < 12 or len(repeated.split()) < 2:
                    continue
                if repeated.lower() in ["для пошуку", "для перевірки", "тестовий текст", "дублікатів"]:
                    continue

                if repeated not in duplicates:
                    duplicates[repeated] = []
                if pos1 not in duplicates[repeated]:
                    duplicates[repeated].append(pos1)
                if pos2 not in duplicates[repeated]:
                    duplicates[repeated].append(pos2)

        return duplicates, []


class SemanticSearch:
    """SemanticSearch — виправлений і покращений для реальних дублікатів"""

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def find_duplicates(self, text):
        """Покращений семантичний пошук: синоніми + подібні фрази"""
        if not text:
            print("Текст відсутній для семантичного пошуку")
            return {}, []

        # Токенізація
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]

        if len(tokens) < 3:
            return {}, []

        duplicates = {}
        positions = []

        # 1. Пошук повторюваних n-gram (2-4 слова)
        for n in range(2, 5):
            ngrams = {}
            for i in range(len(tokens) - n + 1):
                phrase = ' '.join(tokens[i:i+n])
                if phrase in ngrams:
                    ngrams[phrase].append(i)
                else:
                    ngrams[phrase] = [i]
            
            for phrase, pos_list in ngrams.items():
                if len(pos_list) > 1:
                    duplicates[phrase] = pos_list

        # 2. Семантичні групи (синоніми)
        from collections import defaultdict
        lemma_to_words = defaultdict(list)
        
        for token in tokens:
            synsets = wordnet.synsets(token)
            if synsets:
                lemma = synsets[0].lemmas()[0].name()
                lemma_to_words[lemma].append(token)
        
        for lemma, word_list in lemma_to_words.items():
            unique_words = set(word_list)
            if len(unique_words) > 1:  # різні слова з однаковим значенням
                key = f"синоніми: {lemma}"
                duplicates[key] = list(unique_words)

        # 3. Позиції для підсвітки
        for i, token in enumerate(tokens):
            pos = text.lower().find(token)
            if pos != -1:
                positions.append((token, pos))

        print(f"Semantic duplicates found: {len(duplicates)}")
        return duplicates, positions


class FuzzyMatchSearch:
    """Fuzzy Matching algorithm - finds similar but not identical text patterns"""
    
    def __init__(self, threshold=0.85):
        self.threshold = threshold
        self.stop_words = set(stopwords.words('english'))

    def _similarity_ratio(self, s1, s2):
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

    def find_duplicates(self, text):
        """Find similar text patterns using fuzzy matching"""
        if not text:
            print("Текст відсутній для fuzzy matching")
            return {}, []
        
        # Split text into sentences/lines
        lines = text.split('\n')
        original_lines = lines.copy()
        lines = [line.strip() for line in lines if line.strip()]
        
        if len(lines) < 2:
            return {}, []
        
        duplicates = {}
        positions = []
        
        # Compare each line with others
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                similarity = self._similarity_ratio(lines[i], lines[j])
                
                # If similarity is above threshold, it's a fuzzy duplicate
                if similarity >= self.threshold:
                    # Use the actual line as key for highlighting
                    key = lines[i]
                    if key not in duplicates:
                        duplicates[key] = []
                    
                    # Find actual character positions in original text
                    pos_i = text.find(lines[i])
                    pos_j = text.find(lines[j])
                    
                    if pos_i != -1 and pos_i not in duplicates[key]:
                        duplicates[key].append(pos_i)
                    if pos_j != -1 and pos_j not in duplicates[key]:
                        duplicates[key].append(pos_j)
        
        # Build positions list
        for pattern, pos_list in duplicates.items():
            if pos_list:
                positions.append((pattern, pos_list[0]))
        
        print(f"Fuzzy Match duplicates found: {len(duplicates)}")
        return duplicates, positions


class NGramAnalysis:
    """N-gram analysis algorithm - finds repeated word sequences and patterns"""
    
    def __init__(self, n=3):
        self.n = n
        self.stop_words = set(stopwords.words('english'))

    def _extract_ngrams(self, text, n):
        """Extract n-grams from text"""
        tokens = [word.lower() for word in word_tokenize(text) 
                  if word.lower() not in self.stop_words and word.isalnum()]
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)
        
        return ngrams

    def find_duplicates(self, text):
        """Find repeated n-gram patterns"""
        if not text:
            print("Текст відсутній для n-gram аналізу")
            return {}, []
        
        duplicates = {}
        positions = []
        
        # Analyze different n-gram sizes (2-grams, 3-grams, 4-grams)
        for n in range(2, min(5, len(text.split()) // 2)):
            ngrams = self._extract_ngrams(text, n)
            ngram_counts = Counter(ngrams)
            
            # Keep only repeated n-grams
            for ngram, count in ngram_counts.items():
                if count > 1:
                    # Find positions of this n-gram in original text
                    pos_list = []
                    search_text = text.lower()
                    ngram_lower = ngram.lower()
                    start = 0
                    while True:
                        pos = search_text.find(ngram_lower, start)
                        if pos == -1:
                            break
                        pos_list.append(pos)
                        start = pos + 1
                    
                    if ngram not in duplicates and pos_list:
                        duplicates[ngram] = pos_list
        
        # Build positions list
        for pattern, pos_list in duplicates.items():
            if pos_list:
                positions.append((pattern, pos_list[0]))
        
        print(f"N-gram duplicates found: {len(duplicates)}")
        return duplicates, positions


class DocumentationAnalysis:
    """Documentation-specific algorithm - finds repeated documentation patterns"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Common documentation patterns
        self.doc_patterns = [
            'parameter', 'argument', 'return', 'returns', 'example', 'usage',
            'description', 'note', 'warning', 'error', 'exception', 'raises',
            'see also', 'deprecated', 'version', 'author', 'since'
        ]

    def _extract_doc_sections(self, text):
        """Extract documentation sections"""
        sections = {}
        lines = text.split('\n')
        current_section = 'general'
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect section headers
            for pattern in self.doc_patterns:
                if pattern in line_lower:
                    current_section = pattern
                    break
            
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(line)
        
        return sections

    def _find_repeated_patterns(self, text):
        """Find repeated patterns in documentation"""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        duplicates = {}
        
        # Find similar paragraphs
        for i in range(len(paragraphs)):
            for j in range(i + 1, len(paragraphs)):
                # Calculate similarity
                ratio = SequenceMatcher(None, paragraphs[i].lower(), 
                                       paragraphs[j].lower()).ratio()
                
                # If similarity > 0.7, mark as duplicate
                if ratio > 0.7:
                    key = f"Repeated doc: {paragraphs[i][:40]}..."
                    if key not in duplicates:
                        duplicates[key] = []
                    duplicates[key].extend([i, j])
        
        return duplicates

    def find_duplicates(self, text):
        """Find repeated documentation patterns"""
        if not text:
            print("Текст відсутній для аналізу документації")
            return {}, []
        
        duplicates = {}
        positions = []
        
        # Find repeated patterns
        pattern_duplicates = self._find_repeated_patterns(text)
        duplicates.update(pattern_duplicates)
        
        # Find repeated sections
        sections = self._extract_doc_sections(text)
        for section, lines in sections.items():
            if len(lines) > 3:  # If section has multiple lines
                # Check for repeated content within section
                section_text = '\n'.join(lines)
                tokens = [word.lower() for word in word_tokenize(section_text)
                         if word.lower() not in self.stop_words and word.isalnum()]
                
                # Find repeated words in section
                word_counts = Counter(tokens)
                repeated_words = {word: count for word, count in word_counts.items() 
                                 if count > 2}
                
                if repeated_words:
                    key = f"Repeated in {section}: {', '.join(list(repeated_words.keys())[:3])}"
                    duplicates[key] = list(range(len(lines)))
        
        # Build positions list
        for pattern, pos_list in duplicates.items():
            if pos_list:
                positions.append((pattern, pos_list[0] if isinstance(pos_list[0], int) else 0))
        
        print(f"Documentation duplicates found: {len(duplicates)}")
        return duplicates, positions
