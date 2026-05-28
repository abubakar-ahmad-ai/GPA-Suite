"""
ui/app.py
---------
Main ProApp window: toolbar, notebook tabs, status bar, theme switcher.
"""

import tkinter as tk
from tkinter import ttk
from ui.theme_manager import apply_theme, set_theme_root
from ui.themes import THEME_NAMES, get_theme
from ui.widgets.scale_editor import ScaleEditorWindow
from ui.tabs import (SingleSemesterTab, SGPAOnlyTab,
                     MultiSemesterTab, TargetPlannerTab)
from core.gpa_scale import load_scale


class ProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Professional GPA Suite")
        self.geometry("1200x760")
        self.minsize(1000, 660)

        self._theme_name = "light"
        self.scale = load_scale()
        set_theme_root(self)
        self.palette = get_theme(self._theme_name)

        self._build_toolbar()
        self._build_tabs()
        self._build_statusbar()
        self._bind_shortcuts()
        self.palette = apply_theme(self._theme_name)

    # ── Toolbar ──────────────────────────────────────────
    def _build_toolbar(self):
        bar = ttk.Frame(self, style="Surface.TFrame", padding=(14, 8, 14, 6))
        bar.pack(fill="x")

        # App title
        tk.Label(bar,
                 text="📊 Professional GPA Suite",
                 bg=self.palette["surface"],
                 fg=self.palette["accent"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")

        # Right-side buttons
        def tbtn(text, cmd, accent=False):
            style = "Accent.TButton" if accent else "TButton"
            ttk.Button(bar, text=text, command=cmd,
                       style=style).pack(side="right", padx=4)

        tbtn("☀ Light / 🌙 Dark", self._cycle_theme)
        tbtn("⚖  GPA Scale",      self._open_scale_editor, accent=True)

        # Theme label
        self._theme_lbl = tk.Label(bar, text="Theme: Light",
                                    bg=self.palette["surface"],
                                    fg=self.palette["fg_muted"],
                                    font=("Segoe UI", 9))
        self._theme_lbl.pack(side="right", padx=8)

    # ── Tabs ─────────────────────────────────────────────
    def _build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(4, 0))

        self.tab_single = SingleSemesterTab(self.nb, self)
        self.tab_sgpa   = SGPAOnlyTab(self.nb, self)
        self.tab_multi  = MultiSemesterTab(self.nb, self)
        self.tab_target = TargetPlannerTab(self.nb, self)

        self.nb.add(self.tab_single, text=" 📘 Single Semester ")
        self.nb.add(self.tab_sgpa,   text=" 📊 Semesters by SGPA ")
        self.nb.add(self.tab_multi,  text=" 📂 Multi-Semester ")
        self.nb.add(self.tab_target, text=" 🎯 Target CGPA Planner ")

    # ── Status bar ───────────────────────────────────────
    def _build_statusbar(self):
        self._status_var = tk.StringVar(value="Ready")
        bar = ttk.Label(self,
                        textvariable=self._status_var,
                        style="Status.TLabel",
                        anchor="w")
        bar.pack(fill="x", side="bottom")

    def set_status(self, text: str):
        self._status_var.set(text)

    # ── Keyboard shortcuts ───────────────────────────────
    def _bind_shortcuts(self):
        self.bind_all("<Control-d>",  lambda e: self._cycle_theme())
        self.bind_all("<F5>",         lambda e: self.tab_single.recalculate())
        self.bind_all("<Control-s>",  lambda e: self.tab_single._save_csv())
        self.bind_all("<Control-o>",  lambda e: self.tab_single._open_csv())
        self.bind_all("<Control-e>",  lambda e: self._open_scale_editor())

    # ── Theme ────────────────────────────────────────────
    def _cycle_theme(self):
        themes = THEME_NAMES
        idx = (themes.index(self._theme_name) + 1) % len(themes)
        self._theme_name = themes[idx]
        self.palette = apply_theme(self._theme_name)
        self.set_status(f"Theme changed to {self._theme_name}.")

    # ── Scale editor ─────────────────────────────────────
    def _open_scale_editor(self):
        ScaleEditorWindow(self, self)

    def on_scale_changed(self):
        """Called by ScaleEditorWindow after saving."""
        for tab in (self.tab_single, self.tab_sgpa,
                    self.tab_multi, self.tab_target):
            if hasattr(tab, "recalculate"):
                try:
                    tab.recalculate()
                except Exception:
                    pass
            if hasattr(tab, "recalculate_all"):
                try:
                    tab.recalculate_all()
                except Exception:
                    pass
        self.set_status("GPA scale updated — all tabs recalculated.")

    def refresh_theme(self):
        self._theme_lbl.config(
            text=f"Theme: {self._theme_name.title()}",
            bg=self.palette["surface"],
            fg=self.palette["fg_muted"],
        )
