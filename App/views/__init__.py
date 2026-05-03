# Import Premium UI (primary)
try:
    from .premium_login_view import PremiumLoginView
    from .premium_main_view import PremiumMainView
    HAS_PREMIUM_VIEW = True
except ImportError:
    HAS_PREMIUM_VIEW = False
    # Fallback to standard UI
    from .login_view import LoginView as PremiumLoginView
    from .main_view import MainView as PremiumMainView

from .history_window import HistoryWindow

__all__ = ['PremiumLoginView', 'PremiumMainView', 'HistoryWindow']

# For backward compatibility, also export as LoginView and MainView
LoginView = PremiumLoginView
MainView = PremiumMainView
__all__.extend(['LoginView', 'MainView'])
