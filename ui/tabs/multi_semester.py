"""
ui/tabs/multi_semester.py
-------------------------
Tab 3: Multi-Semester Detailed — add semesters one-by-one,
each with its own subject table. Save/Load project as JSON.
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core import compute_cgpa, grade_letter, safe_float
from ui.widgets.semester_panel import SemesterPanel


class MultiSemesterTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.panels = []
        self._build_ui()

    def _build_ui(self):
        # ── Toolbar ──────────────────────────────────────
        bar = ttk.Frame(self, style="Surface.TFrame", padding=(10, 8))
        bar.pack(fill="x")

        ttk.Button(bar, text="＋ Add Semester",
                   command=self._add_semester,
                   style="Accent.TButton").pack(side="left", padx=4)
        ttk.Button(bar, text="－ Remove Last",
                   command=self._remove_last).pack(side="left", padx=4)
        ttk.Button(bar, text="⟳ Recalculate All",
                   command=self.recalculate_all).pack(side="left", padx=4)
        ttk.Button(bar, text="💾 Save Project",
                   command=self._save_project).pack(side="right", padx=4)
        ttk.Button(bar, text="📂 Open Project",
                   command=self._open_project).pack(side="right", padx=4)

        ttk.Label(self,
                  text="Add semesters one by one. Each has its own subject table. CGPA is weighted across all semesters.",
                  style="Sub.TLabel", padding=(12, 4)).pack(anchor="w")

        # ── Scrollable area ──────────────────────────────
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0,
                                bg=self.app.palette["bg"])
        vsb = ttk.Scrollbar(container, orient="vertical",
                            command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.inner = ttk.Frame(self.canvas)
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))
        self._cwin = self.canvas.create_window((0, 0), window=self.inner,
                                               anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(
                             self._cwin, width=e.width))
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        # Mouse wheel scroll
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(
                                 -1 * (e.delta // 120), "units"))

        # ── CGPA bar ─────────────────────────────────────
        p = self.app.palette
        self.bar2 = tk.Frame(self, bg=p["accent"])
        self.bar2.pack(fill="x", side="bottom")
        self.lbl_cgpa = tk.Label(self.bar2, text="Overall CGPA: —",
                                  bg=p["accent"], fg=p["on_accent"],
                                  font=("Segoe UI", 15, "bold"), padx=16, pady=10)
        self.lbl_cgpa.pack(side="right")
        self.lbl_grade = tk.Label(self.bar2, text="",
                                   bg=p["accent"], fg=p["on_accent"],
                                   font=("Segoe UI", 10), padx=14)
        self.lbl_grade.pack(side="right")
        self.lbl_info = tk.Label(self.bar2, text="No semesters yet.",
                                  bg=p["accent"], fg=p["status_muted"],
                                  font=("Segoe UI", 10), padx=16)
        self.lbl_info.pack(side="left")

    # ── Semester management ──────────────────────────────
    def _add_semester(self):
        idx = len(self.panels) + 1
        panel = SemesterPanel(self.inner, self.app, idx)
        panel.pack(fill="x", pady=4, padx=6)
        self.panels.append(panel)
        self.canvas.yview_moveto(1.0)
        self.recalculate_all()

    def _remove_last(self):
        if not self.panels:
            return
        p = self.panels.pop()
        p.destroy()
        self.recalculate_all()

    def recalculate_all(self):
        semesters = []
        for panel in self.panels:
            panel.recalculate()
            for r in panel.tree.get_children():
                g = safe_float(panel.tree.set(r, "gpa"),  None)
                c = safe_float(panel.tree.set(r, "crhr"), None)
                if g is None or c is None or c <= 0:
                    continue
                semesters.append({"gpa": g, "credits": c})

        if semesters:
            cgpa, tot_cr, tot_pts = compute_cgpa(semesters)
            self.lbl_cgpa.config( text=f"Overall CGPA: {cgpa:.2f}")
            self.lbl_grade.config(text=f"Grade: {grade_letter(cgpa)}")
            self.lbl_info.config(
                text=f"Semesters: {len(self.panels)}   "
                     f"Total Credits: {tot_cr:.0f}   "
                     f"Total Points: {tot_pts:.2f}")
        else:
            self.lbl_cgpa.config( text="Overall CGPA: —")
            self.lbl_grade.config(text="")
            n = len(self.panels)
            self.lbl_info.config(
                text=f"{n} semester(s) added — fill in data to calculate.")
        self.app.set_status("Multi-semester recalculated.")

    # ── Save / Load ──────────────────────────────────────
    def _save_project(self):
        path = filedialog.asksaveasfilename(
            title="Save Project", defaultextension=".json",
            filetypes=[("JSON Project", "*.json")])
        if not path: return
        data = {"semesters": [p.to_dict() for p in self.panels]}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", f"Project saved:\n{path}")
        except Exception as ex:
            messagebox.showerror("Save Project", str(ex))

    def _open_project(self):
        path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON Project", "*.json")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for p in self.panels:
                p.destroy()
            self.panels.clear()
            for i, sem in enumerate(data.get("semesters", []), start=1):
                panel = SemesterPanel(self.inner, self.app, i)
                panel.pack(fill="x", pady=4, padx=6)
                panel.load_from(sem)
                self.panels.append(panel)
            self.recalculate_all()
        except Exception as ex:
            messagebox.showerror("Open Project", str(ex))

    def refresh_theme(self):
        p = self.app.palette
        self.canvas.configure(bg=p["bg"])
        self.bar2.config(bg=p["accent"])
        for w in (self.lbl_cgpa, self.lbl_grade, self.lbl_info):
            w.config(bg=p["accent"])
        for panel in self.panels:
            panel.refresh_theme()
