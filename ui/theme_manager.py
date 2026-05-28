"""
ui/theme_manager.py
-------------------
Global theme application and widget refresh helpers.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .themes import THEME_NAMES, get_current_theme_name, get_theme, set_current_theme
from .ui_styles import configure_styles

_THEME_ROOT: tk.Misc | None = None


def set_theme_root(root: tk.Misc):
    global _THEME_ROOT
    _THEME_ROOT = root


def get_theme_root() -> tk.Misc | None:
    return _THEME_ROOT


def apply_theme(theme_name: str, root: tk.Misc | None = None):
    widget_root = root or _THEME_ROOT
    if widget_root is None:
        raise RuntimeError("No theme root registered. Call set_theme_root(root) first.")

    theme = get_theme(theme_name)
    set_current_theme(theme_name)
    widget_root.palette = theme
    widget_root._theme_name = theme_name

    style = ttk.Style(widget_root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    widget_root.configure(bg=theme["window_bg"])
    configure_styles(style, theme)
    _apply_widget_tree(widget_root, theme)
    _refresh_hooks(widget_root)
    return theme


def _refresh_hooks(widget: tk.Misc):
    hook = getattr(widget, "refresh_theme", None)
    if callable(hook):
        try:
            hook()
        except Exception:
            pass
    for child in widget.winfo_children():
        _refresh_hooks(child)


def _apply_widget_tree(widget: tk.Misc, theme: dict):
    _apply_single_widget(widget, theme)
    for child in widget.winfo_children():
        _apply_widget_tree(child, theme)


def _apply_single_widget(widget: tk.Misc, theme: dict):
    if isinstance(widget, ttk.Widget):
        _apply_ttk_widget(widget, theme)
        return

    widget_class = widget.winfo_class()
    role = getattr(widget, "_theme_role", None)

    if isinstance(widget, (tk.Tk, tk.Toplevel)):
        widget.configure(bg=theme["window_bg"])
    elif isinstance(widget, tk.Frame):
        widget.configure(bg=_frame_bg(widget, widget_class, role, theme))
    elif isinstance(widget, tk.Label):
        _configure_label(widget, role, theme)
    elif isinstance(widget, tk.Button):
        _configure_button(widget, role, theme)
    elif isinstance(widget, tk.Entry):
        _configure_entry(widget, role, theme)
    elif isinstance(widget, tk.Canvas):
        widget.configure(bg=_canvas_bg(role, theme))
    elif isinstance(widget, tk.Scrollbar):
        widget.configure(
            bg=theme["scrollbar_bg"],
            troughcolor=theme["scrollbar_trough"],
            activebackground=theme["scrollbar_active"],
            highlightthickness=0,
        )


def _apply_ttk_widget(widget: ttk.Widget, theme: dict):
    widget_class = widget.winfo_class()
    if widget_class == "Treeview":
        for tag in ("odd", "even"):
            try:
                widget.tag_configure(tag, background=theme["tree_bg"] if tag == "odd" else theme["tree_alt_bg"])
            except Exception:
                pass
    elif widget_class == "TNotebook":
        pass


def _frame_bg(widget, widget_class, role, theme):
    value = getattr(widget, "_theme_bg", None) or widget.cget("bg")
    return _map_color(value, theme, role, (
        "window_bg", "surface", "surface_alt", "surface_soft", "card_bg",
        "card_alt_bg", "hint_bg", "status_bg", "footer_bg", "accent",
        "table_bg", "table_alt_bg", "card_header_bg",
    ), default=theme["window_bg"])


def _canvas_bg(role, theme):
    if role in {"surface", "card", "table"}:
        return theme["surface"]
    if role == "accent":
        return theme["accent"]
    return theme["window_bg"]


def _configure_label(widget: tk.Label, role, theme: dict):
    current_bg = widget.cget("bg")
    current_fg = widget.cget("fg")
    bg = _map_color(current_bg, theme, role, (
        "window_bg", "surface", "surface_alt", "surface_soft", "card_bg",
        "card_alt_bg", "hint_bg", "status_bg", "footer_bg", "accent",
        "table_bg", "table_alt_bg", "card_header_bg", "gpa_card_bg",
        "grade_card_bg", "points_card_bg", "info_card_bg",
    ), default=current_bg)
    fg = _map_color(current_fg, theme, role, (
        "text", "text_muted", "text_soft", "accent_fg", "on_accent",
        "success", "warning", "danger", "info", "purple", "teal", "amber",
        "brown", "status_fg", "status_muted", "hint_fg", "table_header_fg",
        "tree_heading_fg", "gpa_card_fg", "grade_card_fg", "points_card_fg",
        "info_card_fg", "tab_active_fg", "footer_fg", "button_primary_fg",
        "button_secondary_fg", "button_success_fg", "button_danger_fg",
        "button_muted_fg", "button_ghost_fg", "table_selected_fg",
    ), default=current_fg)
    widget.configure(bg=bg, fg=fg)


def _configure_button(widget: tk.Button, role, theme: dict):
    current_bg = widget.cget("bg")
    current_fg = widget.cget("fg")
    bg = _map_color(current_bg, theme, role, (
        "button_primary_bg", "button_secondary_bg", "button_success_bg",
        "button_danger_bg", "button_muted_bg", "button_ghost_bg",
        "accent", "surface", "surface_alt", "status_bg",
    ), default=current_bg)
    fg = _map_color(current_fg, theme, role, (
        "button_primary_fg", "button_secondary_fg", "button_success_fg",
        "button_danger_fg", "button_muted_fg", "button_ghost_fg",
        "text", "text_muted", "on_accent",
    ), default=current_fg)
    active_bg = _button_active_bg(bg, theme)
    widget.configure(
        bg=bg,
        fg=fg,
        activebackground=active_bg,
        activeforeground=fg,
        relief="flat",
        highlightthickness=0,
    )


def _configure_entry(widget: tk.Entry, role, theme: dict):
    current_bg = widget.cget("bg")
    bg = _map_color(current_bg, theme, role, (
        "entry_bg", "entry_warning_bg", "entry_success_bg", "entry_info_bg",
        "surface", "surface_alt", "card_bg",
    ), default=current_bg)
    fg = _map_color(widget.cget("fg"), theme, role, (
        "entry_fg", "placeholder", "text", "text_muted",
    ), default=widget.cget("fg"))
    widget.configure(
        bg=bg,
        fg=fg,
        insertbackground=theme["entry_fg"],
        highlightbackground=theme["entry_border"],
        highlightcolor=theme["entry_focus"],
        disabledforeground=theme["text_soft"],
    )


def _button_active_bg(bg, theme):
    if bg == theme["button_primary_bg"] or bg == theme["accent"]:
        return theme["button_primary_hover"]
    if bg == theme["button_success_bg"]:
        return theme["button_success_hover"]
    if bg == theme["button_danger_bg"]:
        return theme["button_danger_hover"]
    if bg == theme["button_muted_bg"]:
        return theme["button_muted_hover"]
    if bg == theme["button_ghost_bg"] or bg == theme["button_secondary_bg"]:
        return theme["button_secondary_hover"]
    return theme["accent_hover"]


def _map_color(value, theme, role, candidates, default=None):
    if role:
        if role in theme:
            return theme[role]
        if f"{role}_bg" in theme:
            return theme[f"{role}_bg"]
        if f"{role}_fg" in theme:
            return theme[f"{role}_fg"]
    for key in candidates:
        if key in theme and value == theme[key]:
            return theme[key]
    return default


def refresh_all(root: tk.Misc | None = None):
    target = root or _THEME_ROOT
    if target is None:
        return
    apply_theme(get_current_theme_name(), target)
