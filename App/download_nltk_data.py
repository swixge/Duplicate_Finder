#!/usr/bin/env python3
"""Download required NLTK data"""

import nltk
import sys

print("Завантаження NLTK ресурсів...")

try:
    print("\n1. Завантаження 'punkt'...")
    nltk.download('punkt', quiet=False)
    print("   ✓ 'punkt' завантажено")
except Exception as e:
    print(f"   ✗ Помилка: {e}")
    sys.exit(1)

try:
    print("\n2. Завантаження 'wordnet'...")
    nltk.download('wordnet', quiet=False)
    print("   ✓ 'wordnet' завантажено")
except Exception as e:
    print(f"   ✗ Помилка: {e}")
    sys.exit(1)

try:
    print("\n3. Завантаження 'stopwords'...")
    nltk.download('stopwords', quiet=False)
    print("   ✓ 'stopwords' завантажено")
except Exception as e:
    print(f"   ✗ Помилка: {e}")
    sys.exit(1)

try:
    print("\n4. Завантаження 'punkt_tab' (новіша версія punkt)...")
    nltk.download('punkt_tab', quiet=False)
    print("   ✓ 'punkt_tab' завантажено")
except Exception as e:
    print(f"   ✗ Помилка: {e}")
    sys.exit(1)

try:
    print("\n5. Завантаження 'omw-1.4' (Open Multilingual Wordnet)...")
    nltk.download('omw-1.4', quiet=False)
    print("   ✓ 'omw-1.4' завантажено")
except Exception as e:
    print(f"   ✗ Помилка: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✓ Всі NLTK ресурси успішно завантажені!")
print("="*50)
print("\nТепер ви можете запустити додаток:")
print("  python main.py")
