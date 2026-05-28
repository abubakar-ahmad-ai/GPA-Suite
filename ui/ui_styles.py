"""
ui/ui_styles.py
---------------
Central ttk style configuration helpers.
"""

from tkinter import ttk

from .themes import FONTS


def style_card(style: ttk.Style, theme: dict):
    style.configure("TFrame", background=theme["window_bg"])
    style.configure("Surface.TFrame", background=theme["surface"])
    style.configure("Surface2.TFrame", background=theme["surface_alt"])
    style.configure(
        "Card.TFrame",
        background=theme["card_bg"],
        relief="flat",
        borderwidth=1,
    )
    style.configure("Header.TFrame", background=theme["card_header_bg"])
    style.configure("Footer.TFrame", background=theme["footer_bg"])


def style_label(style: ttk.Style, theme: dict):
    style.configure(
        "TLabel",
        background=theme["window_bg"],
        foreground=theme["text"],
        font=FONTS["body"],
    )
    style.configure(
        "Title.TLabel",
        background=theme["window_bg"],
        foreground=theme["text"],
        font=FONTS["title"],
    )
    style.configure(
        "Heading.TLabel",
        background=theme["window_bg"],
        foreground=theme["text"],
        font=FONTS["heading"],
    )
    style.configure(
        "Sub.TLabel",
        background=theme["window_bg"],
        foreground=theme["text_muted"],
        font=FONTS["body"],
    )
    style.configure(
        "Muted.TLabel",
        background=theme["window_bg"],
        foreground=theme["text_muted"],
        font=FONTS["small"],
    )
    style.configure(
        "Card.TLabel",
        background=theme["card_bg"],
        foreground=theme["text"],
        font=FONTS["body"],
    )
    style.configure(
        "CardHeading.TLabel",
        background=theme["card_bg"],
        foreground=theme["text"],
        font=FONTS["heading"],
    )
    style.configure(
        "CardSub.TLabel",
        background=theme["card_bg"],
        foreground=theme["text_muted"],
        font=FONTS["small"],
    )
    style.configure(
        "Success.TLabel",
        background=theme["window_bg"],
        foreground=theme["success"],
        font=FONTS["subhead"],
    )
    style.configure(
        "Danger.TLabel",
        background=theme["window_bg"],
        foreground=theme["danger"],
        font=FONTS["subhead"],
    )
    style.configure(
        "Accent.TLabel",
        background=theme["accent"],
        foreground=theme["on_accent"],
        font=FONTS["subhead"],
    )
    style.configure(
        "Status.TLabel",
        background=theme["status_bg"],
        foreground=theme["status_fg"],
        font=FONTS["body"],
        padding=(10, 6),
    )
    style.configure(
        "Footer.TLabel",
        background=theme["footer_bg"],
        foreground=theme["footer_fg"],
        font=FONTS["body"],
    )


def style_button(style: ttk.Style, theme: dict):
    style.configure(
        "TButton",
        background=theme["button_secondary_bg"],
        foreground=theme["button_secondary_fg"],
        font=FONTS["body"],
        padding=(12, 7),
        borderwidth=1,
        relief="flat",
    )
    style.map(
        "TButton",
        background=[("active", theme["button_secondary_hover"]), ("pressed", theme["border"])],
        foreground=[("disabled", theme["text_soft"])],
    )

    style.configure(
        "Accent.TButton",
        background=theme["button_primary_bg"],
        foreground=theme["button_primary_fg"],
        font=FONTS["subhead"],
        padding=(14, 8),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Accent.TButton",
        background=[("active", theme["button_primary_hover"]), ("pressed", theme["button_primary_hover"])],
        foreground=[("disabled", theme["text_soft"])],
    )

    style.configure(
        "Primary.TButton",
        background=theme["button_primary_bg"],
        foreground=theme["button_primary_fg"],
        font=FONTS["subhead"],
        padding=(14, 8),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Primary.TButton",
        background=[("active", theme["button_primary_hover"]), ("pressed", theme["button_primary_hover"])],
    )

    style.configure(
        "Secondary.TButton",
        background=theme["button_secondary_bg"],
        foreground=theme["button_secondary_fg"],
        font=FONTS["body"],
        padding=(12, 7),
        borderwidth=1,
        relief="flat",
    )
    style.map(
        "Secondary.TButton",
        background=[("active", theme["button_secondary_hover"]), ("pressed", theme["border"])],
    )

    style.configure(
        "Success.TButton",
        background=theme["button_success_bg"],
        foreground=theme["button_success_fg"],
        font=FONTS["body"],
        padding=(12, 7),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Success.TButton",
        background=[("active", theme["button_success_hover"]), ("pressed", theme["button_success_hover"])],
    )

    style.configure(
        "Danger.TButton",
        background=theme["button_danger_bg"],
        foreground=theme["button_danger_fg"],
        font=FONTS["body"],
        padding=(12, 7),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Danger.TButton",
        background=[("active", theme["button_danger_hover"]), ("pressed", theme["button_danger_hover"])],
    )

    style.configure(
        "Ghost.TButton",
        background=theme["button_ghost_bg"],
        foreground=theme["button_ghost_fg"],
        font=FONTS["body"],
        padding=(10, 6),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Ghost.TButton",
        background=[("active", theme["button_ghost_hover"])],
        foreground=[("active", theme["text"])],
    )

    style.configure(
        "Icon.TButton",
        background=theme["button_ghost_bg"],
        foreground=theme["button_ghost_fg"],
        font=FONTS["body"],
        padding=(8, 6),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Icon.TButton",
        background=[("active", theme["button_ghost_hover"])],
        foreground=[("active", theme["text"])],
    )


def style_entry(style: ttk.Style, theme: dict):
    style.configure(
        "TEntry",
        fieldbackground=theme["entry_bg"],
        foreground=theme["entry_fg"],
        insertcolor=theme["entry_fg"],
        bordercolor=theme["entry_border"],
        lightcolor=theme["entry_border"],
        darkcolor=theme["entry_border"],
        padding=6,
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", theme["entry_focus"])],
        lightcolor=[("focus", theme["entry_focus"])],
        darkcolor=[("focus", theme["entry_focus"])],
    )

    style.configure(
        "TSpinbox",
        fieldbackground=theme["entry_bg"],
        foreground=theme["entry_fg"],
        insertcolor=theme["entry_fg"],
        bordercolor=theme["entry_border"],
        arrowcolor=theme["text_muted"],
        padding=6,
    )
    style.map(
        "TSpinbox",
        bordercolor=[("focus", theme["entry_focus"])],
    )

    style.configure(
        "TCombobox",
        fieldbackground=theme["entry_bg"],
        background=theme["entry_bg"],
        foreground=theme["entry_fg"],
        arrowcolor=theme["text_muted"],
        bordercolor=theme["entry_border"],
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", theme["entry_bg"])],
        bordercolor=[("focus", theme["entry_focus"])],
    )


def style_table(style: ttk.Style, theme: dict):
    style.configure(
        "Treeview",
        background=theme["tree_bg"],
        foreground=theme["text"],
        fieldbackground=theme["tree_bg"],
        rowheight=32,
        font=FONTS["body"],
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=theme["tree_heading_bg"],
        foreground=theme["tree_heading_fg"],
        font=FONTS["subhead"],
        padding=(8, 6),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", theme["tree_selected_bg"])],
        foreground=[("selected", theme["tree_selected_fg"])],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", theme["accent_hover"])],
        foreground=[("active", theme["on_accent"])],
    )


def style_notebook(style: ttk.Style, theme: dict):
    style.configure(
        "TNotebook",
        background=theme["tab_bar_bg"],
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=theme["tab_bg"],
        foreground=theme["tab_fg"],
        padding=(18, 9),
        font=FONTS["subhead"],
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", theme["tab_active_bg"]), ("active", theme["tab_hover_bg"])],
        foreground=[("selected", theme["tab_active_fg"]), ("active", theme["text"])],
        expand=[("selected", (0, 0, 0, 0))],
    )


def style_scrollbar(style: ttk.Style, theme: dict):
    style.configure(
        "TScrollbar",
        background=theme["scrollbar_bg"],
        troughcolor=theme["scrollbar_trough"],
        borderwidth=0,
        arrowsize=12,
    )
    style.map(
        "TScrollbar",
        background=[("active", theme["scrollbar_active"])],
    )


def configure_styles(style: ttk.Style, theme: dict):
    style_card(style, theme)
    style_label(style, theme)
    style_button(style, theme)
    style_entry(style, theme)
    style_notebook(style, theme)
    style_table(style, theme)
    style_scrollbar(style, theme)
    style.configure("TSeparator", background=theme["border"])
    style.configure(
        "TProgressbar",
        troughcolor=theme["border"],
        background=theme["accent"],
        borderwidth=0,
    )

