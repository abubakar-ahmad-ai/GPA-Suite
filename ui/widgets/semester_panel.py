"""
ui/widgets/semester_panel.py
----------------------------
Reusable collapsible semester panel used in Multi-Semester tab.
"""

import tkinter as tk
from tkinter import ttk
from core import marks_to_gpa, grade_letter, safe_float, compute_sgpa


class SemesterPanel(ttk.Frame):
    def __init__(self, parent, app, sem_index: int):
        super().__init__(parent, style="Card.TFrame")
        self.app = app
        self.sem_index = sem_index
        self.sgpa = 0.0
        self.collapsed = False
        self._build_ui()

    def _build_ui(self):
        p = self.app.palette
        # ── Header bar ──────────────────────────────────
        self.header = tk.Frame(self, bg=p["accent"], cursor="hand2")
        self.header.pack(fill="x")
        self.header.bind("<Button-1>", self._toggle)

        self.toggle_btn = tk.Label(
            self.header, text="▾",
            bg=p["accent"], fg=p["on_accent"],
            font=("Segoe UI", 12, "bold"), cursor="hand2")
        self.toggle_btn.pack(side="left", padx=8, pady=6)
        self.toggle_btn.bind("<Button-1>", self._toggle)

        tk.Label(self.header,
                 text=f"  Semester {self.sem_index}",
                 bg=p["accent"], fg=p["on_accent"],
                 font=("Segoe UI", 11, "bold")).pack(side="left", pady=6)

        self.sgpa_badge = tk.Label(
            self.header, text="SGPA: —",
            bg=p["accent_hover"], fg=p["on_accent"],
            font=("Segoe UI", 10, "bold"),
            padx=10, pady=3)
        self.sgpa_badge.pack(side="right", padx=10, pady=6)

        # ── Body (collapsible) ───────────────────────────
        self.body = tk.Frame(self, bg=p["surface"])
        self.body.pack(fill="x")

        btn_row = tk.Frame(self.body, bg=p["surface"])
        btn_row.pack(fill="x", padx=8, pady=(6, 2))

        def mk_btn(text, cmd, bg=None):
            clr = bg or p["surface2"]
            active = p["accent_hover"] if bg else p["surface"]
            fg = p["on_accent"] if bg else p["fg"]
            tk.Button(btn_row, text=text,
                      bg=clr, fg=fg,
                      activebackground=active,
                      activeforeground=fg,
                      font=("Segoe UI", 9), relief="flat",
                      padx=10, pady=4, cursor="hand2",
                      command=cmd).pack(side="left", padx=3)

        mk_btn("＋ Add Subject", self._add_row)
        mk_btn("－ Remove Last", self._remove_last)
        mk_btn("⟳ Recalculate", self.recalculate, bg=p["accent"])

        # ── Treeview ────────────────────────────────────
        cols = ("subject", "marks", "crhr", "gpa", "grade", "points")
        self.tree = ttk.Treeview(self.body, columns=cols,
                                 show="headings", height=5)
        self.tree.heading("subject", text="Subject")
        self.tree.heading("marks",   text="Marks")
        self.tree.heading("crhr",    text="Cr.Hr")
        self.tree.heading("gpa",     text="GPA")
        self.tree.heading("grade",   text="Grade")
        self.tree.heading("points",  text="Quality Pts")

        self.tree.column("subject", width=200)
        self.tree.column("marks",   width=70,  anchor="center")
        self.tree.column("crhr",    width=60,  anchor="center")
        self.tree.column("gpa",     width=60,  anchor="center")
        self.tree.column("grade",   width=60,  anchor="center")
        self.tree.column("points",  width=90,  anchor="center")
        self.tree.pack(fill="x", padx=8, pady=4)
        self.tree.bind("<Double-1>", self._edit_cell)

        # add 5 default empty rows
        for _ in range(5):
            self._add_row()
        self.refresh_theme()

    def _toggle(self, *_):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.body.pack_forget()
            self.toggle_btn.config(text="▸")
        else:
            self.body.pack(fill="x")
            self.toggle_btn.config(text="▾")

    def _add_row(self):
        row_index = len(self.tree.get_children())
        tag = "odd" if row_index % 2 == 0 else "even"
        self.tree.insert("", "end", values=("", "", "", "—", "—", "—"), tags=(tag,))

    def _remove_last(self):
        children = self.tree.get_children()
        if children:
            self.tree.delete(children[-1])
            self.recalculate()

    def _edit_cell(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        rowid  = self.tree.identify_row(event.y)
        colid  = self.tree.identify_column(event.x)
        col_i  = int(colid.replace("#", "")) - 1
        if col_i >= 3: return  # only subject, marks, crhr editable
        x, y, w, h = self.tree.bbox(rowid, colid)
        val = self.tree.set(rowid, self.tree["columns"][col_i])
        e = ttk.Entry(self.tree)
        e.insert(0, val)
        e.place(x=x, y=y, width=w, height=h)
        e.focus()

        def done(*_):
            nv = e.get().strip()
            e.destroy()
            self.tree.set(rowid, self.tree["columns"][col_i], nv)
            self.recalculate()

        e.bind("<Return>", done)
        e.bind("<FocusOut>", done)
        e.bind("<Escape>", lambda _: e.destroy())

    def recalculate(self):
        subjects = []
        for r in self.tree.get_children():
            m = safe_float(self.tree.set(r, "marks"),  None)
            c = safe_float(self.tree.set(r, "crhr"),   None)
            if m is None or c is None or c <= 0 or not (0 <= m <= 100):
                self.tree.set(r, "gpa",    "—")
                self.tree.set(r, "grade",  "—")
                self.tree.set(r, "points", "—")
                continue
            g = marks_to_gpa(int(round(m)), self.app.scale)
            p_val = g * c
            self.tree.set(r, "gpa",    f"{g:.2f}")
            self.tree.set(r, "grade",  grade_letter(g))
            self.tree.set(r, "points", f"{p_val:.2f}")
            subjects.append({"gpa": g, "credits": c})

        self.sgpa, tot_cr, _ = compute_sgpa(subjects)
        self.sgpa_badge.config(
            text=f"SGPA: {self.sgpa:.2f}  |  Cr: {tot_cr:.0f}")
        for index, row_id in enumerate(self.tree.get_children()):
            self.tree.item(row_id, tags=("odd" if index % 2 == 0 else "even",))

    def refresh_theme(self):
        p = self.app.palette
        self.header.config(bg=p["accent"])
        self.sgpa_badge.config(bg=p["accent_hover"])
        self.body.config(bg=p["surface"])
        self.toggle_btn.config(bg=p["accent"], fg=p["on_accent"])
        self.tree.tag_configure("odd", background=p["tree_bg"])
        self.tree.tag_configure("even", background=p["tree_alt_bg"])

    def to_dict(self):
        rows = []
        for r in self.tree.get_children():
            rows.append({k: self.tree.set(r, k)
                         for k in ("subject", "marks", "crhr", "gpa", "grade", "points")})
        return {"semester": self.sem_index, "rows": rows}

    def load_from(self, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in data.get("rows", []):
            tag = "odd" if len(self.tree.get_children()) % 2 == 0 else "even"
            self.tree.insert("", "end", values=(
                row.get("subject", ""), row.get("marks", ""),
                row.get("crhr", ""),   row.get("gpa", "—"),
                row.get("grade", "—"), row.get("points", "—")), tags=(tag,))
        self.recalculate()
