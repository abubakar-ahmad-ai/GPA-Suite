"""
ui/tabs/single_semester.py  –  Fixed: proper grid alignment, visible boxes
"""
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core import marks_to_gpa, grade_letter, safe_float, compute_sgpa

PH   = {"subject": "Subject Name…", "marks": "0–100", "crhr": "Cr.Hr"}

TABLE_COLS = (
    {"text": "#",              "minsize": 44,  "weight": 0},
    {"text": "Subject Name",   "minsize": 320, "weight": 1},
    {"text": "Marks",          "minsize": 94,  "weight": 0},
    {"text": "Credit Hours",   "minsize": 104, "weight": 0},
    {"text": "GPA",            "minsize": 74,  "weight": 0},
    {"text": "Grade",          "minsize": 74,  "weight": 0},
    {"text": "Quality Points", "minsize": 118, "weight": 0},
)

class SingleSemesterTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._rows = []
        self._build_ui()

    # ── UI scaffold ──────────────────────────────────────
    def _build_ui(self):
        self._build_topbar()
        self._build_hint()
        self._build_col_header()
        self._build_scroll_area()
        self._build_statusbar()
        self._create_rows(5)

    def _build_topbar(self):
        p = self.app.palette
        bar = tk.Frame(self, bg=p["surface"], pady=7)
        bar.pack(fill="x", padx=0)

        tk.Label(bar, text="Subjects:", bg=p["surface"], fg=p["fg"],
                 font=("Segoe UI",10)).pack(side="left", padx=(12,2))
        self.subject_count = tk.IntVar(value=5)
        sp = ttk.Spinbox(bar, from_=1, to=30, width=4,
                         textvariable=self.subject_count,
                         command=self._on_count_change)
        sp.pack(side="left", padx=(0,14))

        for txt, cmd in [("Fill Demo",self._fill_demo),
                         ("Open CSV", self._open_csv),
                         ("Save CSV", self._save_csv),
                         ("Clear",    self._clear)]:
            tk.Button(bar, text=txt, command=cmd,
                      bg=p["surface2"], fg=p["fg"],
                      font=("Segoe UI",9), relief="flat",
                      padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)

        tk.Button(bar, text="⟳  Recalculate", command=self.recalculate,
                  bg=p["accent"], fg=p["on_accent"],
                  font=("Segoe UI",10,"bold"), relief="flat",
                  padx=14, pady=4, cursor="hand2").pack(side="right", padx=10)

    def _build_hint(self):
        p = self.app.palette
        hint = tk.Frame(self, bg=p["hint_bg"], pady=5)
        hint.pack(fill="x")
        tk.Label(hint,
             text="✏  Click a box to type:   Subject Name  →  Marks (0–100)  →  Credit Hours  →  GPA is auto-calculated",
             bg=p["hint_bg"], fg=p["hint_fg"],
             font=("Segoe UI",9,"bold")).pack(side="left", padx=12)

    def _build_col_header(self):
        p = self.app.palette
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
                pady=8,
                anchor="center",
            ).grid(row=0, column=ci, padx=padx, sticky="nsew")

    def _build_scroll_area(self):
        p = self.app.palette
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

        self._cwin = self.canvas.create_window((0,0), window=self.rows_frame,
                                                anchor="nw")
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self._cwin, width=e.width))
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1*(e.delta//120),"units"))

    def _configure_table_columns(self, frame):
        for ci, spec in enumerate(TABLE_COLS):
            frame.columnconfigure(ci, minsize=spec["minsize"], weight=spec["weight"])

    def _build_statusbar(self):
        p = self.app.palette
        self._status_bar = tk.Frame(self, bg=p["accent"])
        self._status_bar.pack(fill="x", side="bottom")

        self.lbl_credits = tk.Label(self._status_bar, text="Total Credits: 0",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",10,"bold"), padx=14, pady=8)
        self.lbl_credits.pack(side="left")
        self.lbl_points = tk.Label(self._status_bar, text="Total Points: 0.00",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",10,"bold"), padx=14)
        self.lbl_points.pack(side="left")
        self.lbl_grade = tk.Label(self._status_bar, text="Grade: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",10,"bold"), padx=14)
        self.lbl_grade.pack(side="right")
        self.lbl_sgpa = tk.Label(self._status_bar, text="SGPA: —",
            bg=p["accent"], fg=p["on_accent"], font=("Segoe UI",15,"bold"), padx=14)
        self.lbl_sgpa.pack(side="right")

    # ── Row creation ─────────────────────────────────────
    def _create_rows(self, n):
        for w in self.rows_frame.winfo_children():
            w.destroy()
        self._rows.clear()
        for i in range(1, n+1):
            self._make_row(i)

    def _make_row(self, idx):
        p = self.app.palette
        row_bg = p["surface"] if idx%2==1 else p["row_alt"]
        r = tk.Frame(self.rows_frame, bg=row_bg,
                     highlightthickness=1,
                     highlightbackground=p["border"])
        r.grid(row=idx-1, column=0, sticky="ew", pady=1)
        self._configure_table_columns(r)

        # ── # label
        tk.Label(r, text=str(idx), bg=row_bg, fg=p["fg_muted"],
                 font=("Segoe UI",10), anchor="center").grid(
                     row=0, column=0, padx=(6, 1), pady=5, sticky="nsew")

        # ── Subject
        e_subj = self._make_entry(r, PH["subject"],
                                   bg=p["entry_bg"], width=28)
        e_subj.grid(row=0, column=1, sticky="nsew",
                    padx=1, pady=5, ipady=4)
        self._bind_ph(e_subj, PH["subject"])

        # ── Marks
        e_marks = self._make_entry(r, PH["marks"],
                                    bg=p["entry_warning_bg"], width=8,
                                    justify="center")
        e_marks.grid(row=0, column=2, sticky="nsew",
                     padx=1, pady=5, ipady=4)
        self._bind_ph(e_marks, PH["marks"], cb=self.recalculate)

        # ── Cr.Hr
        e_crhr = self._make_entry(r, PH["crhr"],
                                   bg=p["entry_success_bg"], width=8,
                                   justify="center")
        e_crhr.grid(row=0, column=3, sticky="nsew",
                    padx=1, pady=5, ipady=4)
        self._bind_ph(e_crhr, PH["crhr"], cb=self.recalculate)

        # ── GPA output
        lbl_gpa = tk.Label(r, text="—",
                            bg=p["gpa_card_bg"], fg=p["gpa_card_fg"],
                            font=("Segoe UI",10,"bold"), anchor="center",
                            relief="flat", bd=0)
        lbl_gpa.grid(row=0, column=4, sticky="nsew",
                     padx=1, pady=5, ipady=4)

        # ── Grade output
        lbl_grade = tk.Label(r, text="—",
                              bg=p["grade_card_bg"], fg=p["grade_card_fg"],
                              font=("Segoe UI",10,"bold"), anchor="center")
        lbl_grade.grid(row=0, column=5, sticky="nsew",
                       padx=1, pady=5, ipady=4)

        # ── Points output
        lbl_pts = tk.Label(r, text="—",
                            bg=p["points_card_bg"], fg=p["points_card_fg"],
                            font=("Segoe UI",10,"bold"), anchor="center")
        lbl_pts.grid(row=0, column=6, sticky="nsew",
                     padx=(1, 6), pady=5, ipady=4)

        self._rows.append({"frame":r,"subject":e_subj,"marks":e_marks,
                            "crhr":e_crhr,"gpa":lbl_gpa,
                            "grade":lbl_grade,"points":lbl_pts})

    def _make_entry(self, parent, ph, bg, width, justify="left"):
        p = self.app.palette
        kw = dict(font=("Segoe UI",10), bg=bg, fg=p["placeholder"],
                  relief="solid", bd=1,
                  insertbackground=p["accent"],
                  justify=justify)
        if width: kw["width"] = width
        e = tk.Entry(parent, **kw)
        e.insert(0, ph)
        return e

    def _bind_ph(self, e, ph, cb=None):
        def fi(_):
            if e.get() == ph:
                e.delete(0,"end")
                e.config(fg=self.app.palette["fg"])
        def fo(_):
            if e.get().strip()=="":
                e.delete(0,"end"); e.insert(0,ph)
                e.config(fg=self.app.palette["placeholder"])
            if cb: cb()
        def kr(_):
            if cb: e.after(80, cb)
        e.bind("<FocusIn>",  fi)
        e.bind("<FocusOut>", fo)
        if cb: e.bind("<KeyRelease>", kr)

    def _val(self, e, ph):
        v = e.get().strip()
        return "" if v==ph else v

    # ── Recalculate ──────────────────────────────────────
    def recalculate(self):
        p = self.app.palette
        subjects = []
        for row in self._rows:
            m = safe_float(self._val(row["marks"], PH["marks"]), None)
            c = safe_float(self._val(row["crhr"],  PH["crhr"]),  None)
            if m is None or c is None or c<=0 or not (0<=m<=100):
                row["gpa"].config(   text="—", fg=p["accent"])
                row["grade"].config( text="—", fg=p["success"])
                row["points"].config(text="—", fg=p["points_card_fg"])
                continue
            g = marks_to_gpa(int(round(m)), self.app.scale)
            gl = grade_letter(g)
            pts = g*c
            fail = g==0.0
            row["gpa"].config(   text=f"{g:.2f}",  fg=p["danger"] if fail else p["accent"])
            row["grade"].config( text=gl,           fg=p["danger"] if fail else p["success"])
            row["points"].config(text=f"{pts:.2f}", fg=p["points_card_fg"])
            subjects.append({"gpa":g,"credits":c})

        sgpa, tot_cr, tot_pts = compute_sgpa(subjects)
        self.lbl_credits.config(text=f"Total Credits: {tot_cr:.0f}")
        self.lbl_points.config( text=f"Total Points: {tot_pts:.2f}")
        if subjects:
            self.lbl_sgpa.config( text=f"SGPA: {sgpa:.2f}")
            self.lbl_grade.config(text=f"Grade: {grade_letter(sgpa)}")
        else:
            self.lbl_sgpa.config( text="SGPA: —")
            self.lbl_grade.config(text="Grade: —")
        self.app.set_status("Single semester recalculated.")

    def _on_count_change(self):
        self._create_rows(self.subject_count.get())
        self.app.set_status(f"Rows: {self.subject_count.get()}")

    def _fill_demo(self):
        demo=[("Data Structures",82,3),("Calculus II",75,3),
              ("Digital Logic",88,3),("English Writing",70,2),("Physics Lab",65,1)]
        self._create_rows(len(demo))
        p = self.app.palette
        for row,(subj,marks,cr) in zip(self._rows,demo):
            for key,val in(("subject",subj),("marks",str(marks)),("crhr",str(cr))):
                row[key].delete(0,"end"); row[key].insert(0,str(val))
                row[key].config(fg=p["fg"])
        self.recalculate()

    def _clear(self):
        self._create_rows(self.subject_count.get())
        for lbl in(self.lbl_credits,self.lbl_points,self.lbl_sgpa,self.lbl_grade):
            lbl.config(text=lbl.cget("text").split(":")[0]+": —")
        self.lbl_credits.config(text="Total Credits: 0")
        self.lbl_points.config( text="Total Points: 0.00")
        self.lbl_sgpa.config(   text="SGPA: —")
        self.lbl_grade.config(  text="Grade: —")

    def _open_csv(self):
        path=filedialog.askopenfilename(title="Open CSV",
            filetypes=[("CSV","*.csv"),("All","*.*")])
        if not path: return
        try:
            with open(path,newline="",encoding="utf-8") as f:
                rows=list(csv.DictReader(f))
            self._create_rows(len(rows))
            p=self.app.palette
            for rw,row in zip(self._rows,rows):
                for key,col in(("subject","Subject"),("marks","Marks"),("crhr","CreditHours")):
                    v=row.get(col,"")
                    rw[key].delete(0,"end"); rw[key].insert(0,v); rw[key].config(fg=p["fg"])
            self.recalculate()
        except Exception as ex: messagebox.showerror("CSV",str(ex))

    def _save_csv(self):
        path=filedialog.asksaveasfilename(title="Save CSV",
            defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not path: return
        try:
            with open(path,"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f)
                w.writerow(["Subject","Marks","CreditHours","GPA","Grade","QualityPoints"])
                for row in self._rows:
                    w.writerow([self._val(row["subject"],PH["subject"]),
                                self._val(row["marks"],  PH["marks"]),
                                self._val(row["crhr"],   PH["crhr"]),
                                row["gpa"].cget("text"),
                                row["grade"].cget("text"),
                                row["points"].cget("text")])
            messagebox.showinfo("Saved",f"Saved:\n{path}")
        except Exception as ex: messagebox.showerror("CSV",str(ex))

    def refresh_theme(self):
        p=self.app.palette
        for lbl in(self.lbl_credits,self.lbl_points,self.lbl_sgpa,self.lbl_grade):
            lbl.config(bg=p["accent"])
        self._status_bar.config(bg=p["accent"])
        self.table_shell.config(bg=p["bg"])
        self.table_view.config(bg=p["bg"])
        self.hdr_frame.config(bg=p["accent"])
        for child in self.hdr_frame.winfo_children():
            child.config(bg=p["accent"], fg=p["on_accent"])
        self.canvas.config(bg=p["surface"])
        self.rows_frame.config(bg=p["surface"])
