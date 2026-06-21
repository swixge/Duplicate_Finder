import nltk
import os

def ensure_nltk_data():
    """Перевіряє та завантажує необхідні дані NLTK один раз"""
    required = ['punkt', 'punkt_tab', 'wordnet', 'stopwords', 'omw-1.4']
    data_path = nltk.data.path[0]
    
    for resource in required:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource in ['punkt', 'punkt_tab'] else f'corpora/{resource}')
        except LookupError:
            print(f"Завантаження NLTK ресурсу: {resource}...")
            nltk.download(resource, quiet=True, download_dir=data_path)
            print(f"✓ {resource} завантажено")