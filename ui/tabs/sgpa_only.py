"""
ui/tabs/sgpa_only.py  –  Visible entry boxes for SGPA + Credit Hours
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core import safe_float, compute_cgpa, grade_letter

PH   = {"sgpa": "0.00–4.00", "crhr": "Cr.Hr"}

TABLE_COLS = (
    {"text": "#",                 "minsize": 44,  "weight": 0},
    {"text": "Semester",          "minsize": 126, "weight": 0},
    {"text": "SGPA",              "minsize": 110, "weight": 0},
    {"text": "Credit Hours",      "minsize": 120, "weight": 0},
    {"text": "Quality Pts",       "minsize": 118, "weight": 0},
    {"text": "Cumulative CGPA",   "minsize": 170, "weight": 1},
)

class SGPAOnlyTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._rows = []
        self._build_ui()

    def _build_ui(self):
        p = self.app.palette

        # ── Top bar ──────────────────────────────────────
        bar = tk.Frame(self, bg=p["surface"], pady=7)
        bar.pack(fill="x")
        tk.Label(bar, text="Number of Semesters:",
                 bg=p["surface"], fg=p["fg"],
                 font=("Segoe UI",10)).pack(side="left", padx=(12,2))
        self.sem_count = tk.IntVar(value=8)
        ttk.Spinbox(bar, from_=1, to=20, width=4,
                    textvariable=self.sem_count,
                    command=self._create_rows).pack(side="left", padx=(0,14))
        for txt, cmd in [("Fill Demo", self._fill_demo),
                         ("Clear",     self._clear)]:
            tk.Button(bar, text=txt, command=cmd,
                      bg=p["surface2"], fg=p["fg"],
                      font=("Segoe UI",9), relief="flat",
                      padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)
        tk.Button(bar, text="⟳  Calculate CGPA", command=self.recalculate,
                  bg=p["accent"], fg=p["on_accent"],
                  font=("Segoe UI",10,"bold"), relief="flat",
                  padx=14, pady=4, cursor="hand2").pack(side="right", padx=10)

        # ── Hint ─────────────────────────────────────────
        hint = tk.Frame(self, bg=p["hint_bg"], pady=5)
        hint.pack(fill="x")
        tk.Label(hint,
                 text="✏  Enter each semester's SGPA and Credit Hours → Cumulative CGPA is calculated automatically",
                 bg=p["hint_bg"], fg=p["hint_fg"],
                 font=("Segoe UI",9,"bold")).pack(side="left", padx=12)

        # ── Column header ────────────────────────────────
        self.table_shell = tk.Frame(self, bg=p["bg"])
        self.table_shell.pack(fill="both", expand=True, padx=8, pady=0)

        self.table_view = tk.Frame(self.table_shell, bg=p["bg"])
        self.table_view.pack(side="left", fill="both", expand=True)

        self.hdr_frame = tk.Frame(self.table_view, bg=p["accent"])
        self.hdr_frame.pack(fill="x", pady=(4, 0))
        self._configure_table_columns(self.hdr_frame)
        for ci, spec in enumerate(TABLE_COLS):
            padx = (6, 1) if ci == 0 else (1, 6) if ci == len(TABLE_COLS) - 1 else 1
            tk.Label(
                self.hdr_frame,
                text=spec["text"],
                bg=p["accent"],
                fg=p["on_accent"],
                font=("Segoe UI", 10, "bold"),
                anchor="center",
                pady=8,
            ).grid(row=0, column=ci, padx=padx, sticky="nsew")

        # ── Scroll area ──────────────────────────────────
        vsb = ttk.Scrollbar(self.table_shell, orient="vertical")
        vsb.pack(side="right", fill="y")
        self.canvas = tk.Canvas(self.table_view, highlightthickness=0, bg=p["surface"])
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=p["surface"])
        self.rows_frame.columnconfigure(0, weight=1)
        self.rows_frame.bind("<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self._cwin = self.canvas.create_window((0,0), window=self.rows_frame, anchor="nw")
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self._cwin, width=e.width))
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1*(e.delta//120),"units"))

        # ── Summary bar ──────────────────────────────────
        self._sum_bar = tk.Frame(self, bg=p["accent"])
        self._sum_bar.pack(fill="x", side="bottom")
        self.lbl_cgpa  = tk.Label(self._sum_bar, text="CGPA: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",16,"bold"), padx=16, pady=9)
        self.lbl_cgpa.pack(side="right")
        self.lbl_grade = tk.Label(self._sum_bar, text="Grade: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",10,"bold"), padx=14)
        self.lbl_grade.pack(side="right")
        self.lbl_info  = tk.Label(self._sum_bar, text="",
            bg=p["accent"], fg=p["status_muted"], font=("Segoe UI",10), padx=16)
        self.lbl_info.pack(side="left")

        self._create_rows()

    # ── Row helpers ──────────────────────────────────────
    def _make_entry(self, parent, ph, bg, width, justify="center"):
        p = self.app.palette
        e = tk.Entry(parent, width=width, font=("Segoe UI",10),
                     bg=bg, fg=p["placeholder"], relief="solid", bd=1,
                     justify=justify, insertbackground=p["accent"])
        e.insert(0, ph)
        return e

    def _bind_ph(self, e, ph, cb=None):
        def fi(_):
            if e.get()==ph:
                e.delete(0,"end"); e.config(fg=self.app.palette["fg"])
        def fo(_):
            if e.get().strip()=="":
                e.delete(0,"end"); e.insert(0,ph); e.config(fg=self.app.palette["placeholder"])
            if cb: cb()
        def kr(_):
            if cb: e.after(80, cb)
        e.bind("<FocusIn>",  fi)
        e.bind("<FocusOut>", fo)
        if cb: e.bind("<KeyRelease>", kr)

    def _val(self, e, ph):
        v = e.get().strip()
        return "" if v==ph else v

    def _configure_table_columns(self, frame):
        for ci, spec in enumerate(TABLE_COLS):
            frame.columnconfigure(ci, minsize=spec["minsize"], weight=spec["weight"])

    def _create_rows(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        self._rows.clear()
        n = self.sem_count.get()
        p = self.app.palette
        for i in range(1, n+1):
            row_bg = p["surface"] if i%2==1 else p["row_alt"]
            r = tk.Frame(self.rows_frame, bg=row_bg,
                         highlightthickness=1,
                         highlightbackground=p["border"])
            r.grid(row=i-1, column=0, sticky="ew", pady=1)
            self._configure_table_columns(r)

            # #
            tk.Label(r, text=str(i), bg=row_bg, fg=p["fg_muted"],
                     font=("Segoe UI",10), anchor="center").grid(
                         row=0, column=0, padx=(6, 1), pady=6, sticky="nsew")
            # Semester label
            tk.Label(r, text=f"Semester {i}", bg=row_bg, fg=p["fg"],
                     font=("Segoe UI",10,"bold"), anchor="center").grid(
                         row=0, column=1, padx=1, pady=6, sticky="nsew")
            # SGPA entry
            e_sgpa = self._make_entry(r, PH["sgpa"], p["entry_warning_bg"], 9)
            e_sgpa.grid(row=0, column=2, padx=1, pady=6, ipady=4, sticky="nsew")
            self._bind_ph(e_sgpa, PH["sgpa"], cb=self.recalculate)
            # CrHr entry
            e_crhr = self._make_entry(r, PH["crhr"], p["entry_success_bg"], 8)
            e_crhr.grid(row=0, column=3, padx=1, pady=6, ipady=4, sticky="nsew")
            self._bind_ph(e_crhr, PH["crhr"], cb=self.recalculate)
            # Quality pts
            lbl_pts = tk.Label(r, text="—",
                                bg=p["points_card_bg"], fg=p["points_card_fg"],
                                font=("Segoe UI",10,"bold"), anchor="center")
            lbl_pts.grid(row=0, column=4, padx=1, pady=6, ipady=4, sticky="nsew")
            # Cumulative CGPA
            lbl_cum = tk.Label(r, text="—",
                                bg=p["gpa_card_bg"], fg=p["gpa_card_fg"],
                                font=("Segoe UI",10,"bold"), anchor="center")
            lbl_cum.grid(row=0, column=5, padx=(1, 6), pady=6, ipady=4, sticky="nsew")

            self._rows.append({"sgpa":e_sgpa,"crhr":e_crhr,
                                "pts":lbl_pts,"cum":lbl_cum})

    # ── Recalculate ──────────────────────────────────────
    def recalculate(self):
        p = self.app.palette
        sems = []
        for row in self._rows:
            g = safe_float(self._val(row["sgpa"], PH["sgpa"]), None)
            c = safe_float(self._val(row["crhr"],  PH["crhr"]),  None)
            if g is None or c is None or c<=0 or not(0<=g<=4.0):
                row["pts"].config(text="—", fg=p["points_card_fg"])
                row["cum"].config(text="—", fg=p["gpa_card_fg"])
                continue
            row["pts"].config(text=f"{g*c:.2f}")
            sems.append({"gpa":g,"credits":c})
            cgpa,_,_ = compute_cgpa(sems)
            row["cum"].config(text=f"{cgpa:.2f}",
                              fg=p["success"] if cgpa>=3.0 else
                                 p["warning"] if cgpa>=2.0 else p["danger"])

        if sems:
            cgpa,tot_cr,tot_pts = compute_cgpa(sems)
            self.lbl_cgpa.config( text=f"CGPA: {cgpa:.2f}")
            self.lbl_grade.config(text=f"Grade: {grade_letter(cgpa)}")
            self.lbl_info.config( text=f"Semesters: {len(sems)}   "
                                       f"Total Credits: {tot_cr:.0f}   "
                                       f"Total Points: {tot_pts:.2f}")
        else:
            self.lbl_cgpa.config( text="CGPA: —")
            self.lbl_grade.config(text="Grade: —")
            self.lbl_info.config( text="")
        self.app.set_status("CGPA recalculated.")

    def _fill_demo(self):
        demo=[(3.20,18),(2.90,17),(3.10,19),(3.50,18),
              (3.30,16),(3.70,18),(3.60,17),(3.80,18)]
        p = self.app.palette
        for row,( g,c) in zip(self._rows, demo):
            row["sgpa"].delete(0,"end"); row["sgpa"].insert(0,str(g)); row["sgpa"].config(fg=p["fg"])
            row["crhr"].delete(0,"end"); row["crhr"].insert(0,str(c)); row["crhr"].config(fg=p["fg"])
        self.recalculate()

    def _clear(self):
        self._create_rows()
        self.lbl_cgpa.config( text="CGPA: —")
        self.lbl_grade.config(text="Grade: —")
        self.lbl_info.config( text="")

    def refresh_theme(self):
        p = self.app.palette
        self.table_shell.config(bg=p["bg"])
        self.table_view.config(bg=p["bg"])
        self.hdr_frame.config(bg=p["accent"])
        for child in self.hdr_frame.winfo_children():
            child.config(bg=p["accent"], fg=p["on_accent"])
        self._sum_bar.config(bg=p["accent"])
        for lbl in(self.lbl_cgpa,self.lbl_grade,self.lbl_info):
            lbl.config(bg=p["accent"])
        self.canvas.config(bg=p["surface"])
        self.rows_frame.config(bg=p["surface"])
