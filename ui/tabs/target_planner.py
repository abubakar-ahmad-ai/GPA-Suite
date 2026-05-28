"""
ui/tabs/target_planner.py  –  Fixed visible boxes + better layout
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core import (safe_float, safe_int, compute_cgpa, required_avg_gpa,
                  strategy_balanced, strategy_progressive,
                  strategy_flexible, strategy_front_loaded)

PH   = {"gpa":"0.00–4.00", "crhr":"Cr.Hr"}

TABLE_COLS = (
    {"text": "#",              "minsize": 44},
    {"text": "Semester",       "minsize": 132},
    {"text": "SGPA Achieved",  "minsize": 180},
    {"text": "Credit Hours",   "minsize": 130},
)

class TargetPlannerTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._rows = []
        self._build_ui()

    def _build_ui(self):
        p = self.app.palette

        # ── Hint ─────────────────────────────────────────
        hint = tk.Frame(self, bg=p["hint_bg"], pady=6)
        hint.pack(fill="x")
        tk.Label(hint,
                 text="🎯  Enter your completed semesters below, set your Target CGPA, then click Calculate Plan",
                 bg=p["hint_bg"], fg=p["hint_fg"],
                 font=("Segoe UI",9,"bold")).pack(side="left", padx=12)

        # ── Controls ─────────────────────────────────────
        ctrl = tk.Frame(self, bg=p["surface"], pady=10)
        ctrl.pack(fill="x")

        def lbl_entry(text, default, width=9):
            tk.Label(ctrl, text=text, bg=p["surface"], fg=p["fg"],
                     font=("Segoe UI",10,"bold")).pack(side="left", padx=(12,3))
            e = tk.Entry(ctrl, width=width,
                         font=("Segoe UI",10), bg=p["entry_warning_bg"],
                         fg=p["fg"], relief="solid", bd=1,
                         insertbackground=p["accent"], justify="center")
            e.insert(0, default)
            e.pack(side="left", padx=(0,12), ipady=4)
            return e

        self.e_target    = lbl_entry("🎯 Target CGPA:", "3.20", 8)
        self.e_total     = lbl_entry("📅 Total Sems:",  "8",    6)
        self.e_completed = lbl_entry("✅ Completed:",   "4",    6)

        tk.Button(ctrl, text="Create Rows", command=self._create_rows,
                  bg=p["surface2"], fg=p["fg"],
                  font=("Segoe UI",9), relief="flat",
                  padx=10, pady=4, cursor="hand2").pack(side="left", padx=4)
        tk.Button(ctrl, text="⟳  Calculate Plan", command=self.calculate,
                  bg=p["accent"], fg=p["on_accent"],
                  font=("Segoe UI",10,"bold"), relief="flat",
                  padx=14, pady=5, cursor="hand2").pack(side="right", padx=12)

        # ── Table shell (header + scroll area) ───────────
        self.table_shell = tk.Frame(self, bg=p["bg"])
        self.table_shell.pack(fill="x", padx=8, pady=(6, 0))

        self.table_view = tk.Frame(self.table_shell, bg=p["bg"])
        self.table_view.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.table_shell, orient="vertical")
        vsb.pack(side="right", fill="y")

        # ── Column header (completed sems table) ─────────
        self.hdr_frame = tk.Frame(self.table_view, bg=p["accent"])
        self.hdr_frame.pack(fill="x")
        self._configure_table_columns(self.hdr_frame)
        for ci, spec in enumerate(TABLE_COLS):
            padx = (6, 1) if ci == 0 else (1, 6) if ci == len(TABLE_COLS) - 1 else 1
            tk.Label(self.hdr_frame, text=spec["text"], bg=p["accent"], fg=p["on_accent"],
                     font=("Segoe UI",10,"bold"),
                     pady=7, anchor="center").grid(
                         row=0, column=ci, padx=padx, sticky="nsew")

        # ── Scroll area (completed sem rows) ─────────────
        self.inp_canvas = tk.Canvas(self.table_view, highlightthickness=0,
                                     bg=p["surface"], height=220)
        self.inp_canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.inp_canvas.yview)
        self.inp_frame = tk.Frame(self.inp_canvas, bg=p["surface"])
        self.inp_frame.columnconfigure(0, weight=1)
        self.inp_frame.bind("<Configure>",
            lambda e: self.inp_canvas.configure(
                scrollregion=self.inp_canvas.bbox("all")))
        self._cwin = self.inp_canvas.create_window(
            (0,0), window=self.inp_frame, anchor="nw")
        self.inp_canvas.bind("<Configure>",
            lambda e: self.inp_canvas.itemconfig(self._cwin, width=e.width))
        self.inp_canvas.pack(fill="x", expand=True)

        # ── Summary strip ─────────────────────────────────
        self._sum = tk.Frame(self, bg=p["accent"])
        self._sum.pack(fill="x", padx=8, pady=4)
        self.lbl_cgpa   = tk.Label(self._sum, text="Current CGPA: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",11,"bold"), padx=14, pady=6)
        self.lbl_cgpa.pack(side="left")
        self.lbl_remain = tk.Label(self._sum, text="Remaining: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",10), padx=14)
        self.lbl_remain.pack(side="left")
        self.lbl_req    = tk.Label(self._sum, text="Required Avg GPA: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",11,"bold"), padx=14)
        self.lbl_req.pack(side="right")

        # ── Strategy cards area ───────────────────────────
        self.cards_frame = tk.Frame(self, bg=p["bg"])
        self.cards_frame.pack(fill="both", expand=True, padx=8, pady=6)

        self._create_rows()

    # ── Helpers ──────────────────────────────────────────
    def _configure_table_columns(self, frame):
        for ci, spec in enumerate(TABLE_COLS):
            frame.columnconfigure(ci, minsize=spec["minsize"])

    def _make_entry(self, parent, ph, bg, width):
        p = self.app.palette
        e = tk.Entry(parent, width=width, font=("Segoe UI",10),
                     bg=bg, fg=p["placeholder"], relief="solid", bd=1,
                     justify="center", insertbackground=p["accent"])
        e.insert(0, ph)
        return e

    def _bind_ph(self, e, ph):
        def fi(_):
            if e.get()==ph:
                e.delete(0,"end"); e.config(fg=self.app.palette["fg"])
        def fo(_):
            if e.get().strip()=="":
                e.delete(0,"end"); e.insert(0,ph); e.config(fg=self.app.palette["placeholder"])
        e.bind("<FocusIn>",  fi)
        e.bind("<FocusOut>", fo)

    def _val(self, e, ph):
        v = e.get().strip()
        return "" if v==ph else v

    def _create_rows(self):
        for w in self.inp_frame.winfo_children():
            w.destroy()
        self._rows.clear()
        n = safe_int(self.e_completed.get().strip(), 0) or 0
        p = self.app.palette
        for i in range(1, n+1):
            row_bg = p["surface"] if i%2==1 else p["row_alt"]
            r = tk.Frame(self.inp_frame, bg=row_bg,
                         highlightthickness=1,
                         highlightbackground=p["border"])
            r.grid(row=i-1, column=0, sticky="ew", pady=1)
            self._configure_table_columns(r)
            # #
            tk.Label(r, text=str(i), bg=row_bg, fg=p["fg_muted"],
                     font=("Segoe UI",10), anchor="center"
                     ).grid(row=0, column=0, padx=(6, 1), pady=6, sticky="nsew")
            # sem label
            tk.Label(r, text=f"Semester {i}", bg=row_bg, fg=p["fg"],
                     font=("Segoe UI",10,"bold"), anchor="center"
                     ).grid(row=0, column=1, padx=1, pady=6, sticky="nsew")
            # SGPA
            e_g = self._make_entry(r, PH["gpa"], p["entry_warning_bg"], 10)
            e_g.grid(row=0, column=2, padx=1, pady=6, ipady=4, sticky="nsew")
            self._bind_ph(e_g, PH["gpa"])
            # CrHr
            e_c = self._make_entry(r, PH["crhr"], p["entry_success_bg"], 8)
            e_c.grid(row=0, column=3, padx=(1, 6), pady=6, ipady=4, sticky="nsew")
            self._bind_ph(e_c, PH["crhr"])
            self._rows.append({"gpa":e_g, "crhr":e_c})

    # ── Calculate ────────────────────────────────────────
    def calculate(self):
        try:
            target   = safe_float(self.e_target.get().strip(), None)
            total    = safe_int(  self.e_total.get().strip(),  None)
            comp     = safe_int(  self.e_completed.get().strip(), None)
            if target is None or not(0<=target<=4):
                raise ValueError("Target CGPA must be 0.0–4.0")
            if total  is None or total<=0:
                raise ValueError("Total semesters must be > 0")
            if comp   is None or comp<0:
                raise ValueError("Completed semesters must be ≥ 0")
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex)); return

        sems = []
        for row in self._rows:
            g = safe_float(self._val(row["gpa"], PH["gpa"]), None)
            c = safe_float(self._val(row["crhr"], PH["crhr"]), None)
            if g is None and c is None: continue
            if g is None or c is None or not(0<=g<=4) or c<=0:
                messagebox.showerror("Input Error",
                    "Fill GPA (0–4.0) and Credits for every completed semester.")
                return
            sems.append({"gpa":g,"credits":c})

        if len(sems) != comp:
            messagebox.showerror("Input Error",
                f"Expected {comp} rows filled, got {len(sems)}.")
            return

        remaining = total - comp
        if remaining < 0:
            messagebox.showerror("Input Error","Completed > Total semesters.")
            return

        if sems:
            cgpa,comp_cr,ach_pts = compute_cgpa(sems)
            avg_cr = comp_cr / len(sems)
        else:
            cgpa,comp_cr,ach_pts,avg_cr = 0.0,0.0,0.0,15.0

        rem_cr   = remaining * avg_cr
        total_cr = comp_cr + rem_cr
        req      = required_avg_gpa(target, total_cr, ach_pts, rem_cr)

        self.lbl_cgpa.config(  text=f"Current CGPA: {cgpa:.2f}")
        self.lbl_remain.config(text=f"Remaining Sems: {remaining}   "
                                    f"Rem. Credits ≈ {rem_cr:.0f}")

        if remaining==0:
            msg = "✔ Target reached!" if cgpa>=target else "No semesters left."
            self.lbl_req.config(text=msg)
            self._clear_cards(); return

        if req is None or req>4.0:
            self.lbl_req.config(text=f"⚠ Not achievable (need >{req:.2f})")
            self._clear_cards(); return

        if cgpa>=target:
            self.lbl_req.config(text="✔ Target already achieved!")
            self._clear_cards(); return

        self.lbl_req.config(text=f"Required Avg GPA: {req:.2f}")
        start = comp+1
        strategies=[
            ("Option 1 – Balanced",     p["strategy_balanced"],     strategy_balanced(    req, remaining)),
            ("Option 2 – Progressive",  p["strategy_progressive"],  strategy_progressive( req, remaining)),
            ("Option 3 – Flexible",     p["strategy_flexible"],     strategy_flexible(    req, remaining)),
            ("Option 4 – Front-Loaded", p["strategy_front_loaded"], strategy_front_loaded(req, remaining)),
        ]
        self._render_cards(strategies, start)
        self.app.set_status("Target plan calculated.")

    def _clear_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

    def _render_cards(self, strategies, start):
        self._clear_cards()
        p = self.app.palette
        for ci,(title,color,values) in enumerate(strategies):
            card = tk.Frame(self.cards_frame, bg=p["surface"],
                            bd=1, relief="solid")
            card.grid(row=0, column=ci, padx=5, pady=2, sticky="nsew")
            self.cards_frame.columnconfigure(ci, weight=1)
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=title, bg=p["surface"], fg=color,
                     font=("Segoe UI",10,"bold"), padx=10, pady=6
                     ).pack(anchor="w")
            for i,v in enumerate(values):
                bg2 = p["surface"] if i%2==0 else p["row_alt"]
                tk.Label(card, text=f"Semester {start+i}:   {v:.2f}",
                         bg=bg2, fg=p["fg"],
                         font=("Segoe UI",10), padx=14, pady=4,
                         anchor="w").pack(fill="x")

    def refresh_theme(self):
        p = self.app.palette
        self._sum.config(bg=p["accent"])
        for lbl in(self.lbl_cgpa,self.lbl_remain,self.lbl_req):
            lbl.config(bg=p["accent"])
        self.table_shell.config(bg=p["bg"])
        self.table_view.config(bg=p["bg"])
        self.hdr_frame.config(bg=p["accent"])
        for child in self.hdr_frame.winfo_children():
            child.config(bg=p["accent"], fg=p["on_accent"])
        self.inp_canvas.config(bg=p["surface"])
        self.inp_frame.config(bg=p["surface"])
