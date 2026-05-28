"""
Compatibility wrapper for the new theme engine.
"""

import tkinter as tk

from .themes import FONTS, THEME_NAMES, THEMES, get_current_theme_name, get_theme, set_current_theme
from .theme_manager import apply_theme as _apply_theme, get_theme_root, refresh_all, set_theme_root


def get_palette(name=None):
    return get_theme(name)


def apply(root_or_name, name: str | None = None):
    if isinstance(root_or_name, tk.Misc):
        set_theme_root(root_or_name)
        return _apply_theme(name or get_current_theme_name(), root_or_name)
    return _apply_theme(root_or_name, name)
