#!/usr/bin/env python3
"""
Duplicate Finder Application
Main entry point for the MVC application
"""

import tkinter as tk
from tkinter import messagebox
import nltk

from controllers import MainController
from views import PremiumLoginView, PremiumMainView, LoginView, MainView
from models.nltk_utils import ensure_nltk_data

def main():
    print("Перевірка та завантаження NLTK даних...")
    ensure_nltk_data()
    print("NLTK готово")

def start_main(role, password, login_root, controller):
    """Start main application after login"""
    print("Викликано start_main з роллю:", role)
    try:
        controller.login(role, password)
        print("Логін успішний, створюю MainView")
        login_root.destroy()
        main_root = tk.Tk()
        main_root.title("Duplicate Finder")
        
        # Use Premium UI (with automatic fallback if needed)
        print("Використовую PremiumMainView")
        main_view = PremiumMainView(main_root, controller)
        
        print("MainView створено")
        main_root.mainloop()
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося увійти: {str(e)}")
        print(f"Помилка в start_main: {str(e)}")


def main():
    """Main application entry point"""
    try:
        print("Завантаження NLTK даних...")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)  # Новіша версія для Python 3.13+
        nltk.download('wordnet', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('omw-1.4', quiet=True)  # Додатковий ресурс для wordnet
        print("NLTK дані завантажено")
    except Exception as e:
        print(f"Помилка завантаження NLTK даних: {str(e)}")
        print("Спробуйте запустити: python download_nltk_data.py")
        exit(1)

    root = tk.Tk()
    controller = MainController()
    
    # Use Premium Login (with automatic fallback if needed)
    print("Використовую PremiumLoginView")
    login_view = PremiumLoginView(root, lambda role, password: start_main(role, password, root, controller))
    
    root.mainloop()


if __name__ == "__main__":
    main()
