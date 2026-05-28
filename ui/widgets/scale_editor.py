"""
ui/widgets/scale_editor.py
--------------------------
Full GUI-based GPA scale editor.
Users can Add, Edit, Delete rows and load preset scales.
No Python code needed — pure table editing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.gpa_scale import (
    save_scale, DEFAULT_SCALE_ROWS, PRESET_SCALES, build_label
)


class ScaleEditorWindow(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("GPA Scale Editor")
        self.geometry("780x580")
        self.minsize(700, 480)
        self.resizable(True, True)
        self._rows = list(app.scale)  # working copy
        self._build_ui()
        self._load_table()
        self.transient(parent)
        self.grab_set()

    def _build_ui(self):
        p = self.app.palette
        self.configure(bg=p["bg"])

        # ── Header ──────────────────────────────────────
        hdr = tk.Frame(self, bg=p["accent"], pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚖  GPA Scale Editor",
                 bg=p["accent"], fg=p["on_accent"],
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=18)
        tk.Label(hdr,
                 text="Edit ranges directly in the table. Changes apply to all tabs.",
                 bg=p["accent"], fg=p["status_muted"],
                 font=("Segoe UI", 9)).pack(side="left", padx=6)

        # ── Preset bar ──────────────────────────────────
        preset_bar = tk.Frame(self, bg=p["surface"], pady=8, padx=14)
        preset_bar.pack(fill="x")
        tk.Label(preset_bar, text="Load Preset:",
                 bg=p["surface"], fg=p["fg"],
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        self.preset_var = tk.StringVar(value="Select a preset...")
        presets = list(PRESET_SCALES.keys())
        cb = ttk.Combobox(preset_bar, textvariable=self.preset_var,
                          values=presets, state="readonly", width=22)
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", self._load_preset)

        tk.Label(preset_bar,
                 text="  or edit manually below",
                 bg=p["surface"], fg=p["fg_muted"],
                 font=("Segoe UI", 9)).pack(side="left")

        # ── Toolbar ─────────────────────────────────────
        toolbar = tk.Frame(self, bg=p["bg"], pady=6, padx=10)
        toolbar.pack(fill="x")

        btn_cfg = dict(font=("Segoe UI", 9, "bold"), relief="flat",
                       cursor="hand2", padx=12, pady=5)

        tk.Button(toolbar, text="＋  Add Row",
                  bg=p["button_success_bg"], fg=p["button_success_fg"],
                  activebackground=p["button_success_hover"],
                  activeforeground=p["button_success_fg"],
                  command=self._add_row, **btn_cfg).pack(side="left", padx=3)
        tk.Button(toolbar, text="✎  Edit Selected",
                  bg=p["accent"], fg=p["on_accent"],
                  activebackground=p["accent_hover"],
                  activeforeground=p["on_accent"],
                  command=self._edit_selected, **btn_cfg).pack(side="left", padx=3)
        tk.Button(toolbar, text="✕  Delete Selected",
                  bg=p["button_danger_bg"], fg=p["button_danger_fg"],
                  activebackground=p["button_danger_hover"],
                  activeforeground=p["button_danger_fg"],
                  command=self._delete_selected, **btn_cfg).pack(side="left", padx=3)
        tk.Button(toolbar, text="↺  Reset to Default",
                  bg=p["button_muted_bg"], fg=p["button_muted_fg"],
                  activebackground=p["button_muted_hover"],
                  activeforeground=p["button_muted_fg"],
                  command=self._reset_default, **btn_cfg).pack(side="left", padx=3)

        # ── Table ────────────────────────────────────────
        table_frame = tk.Frame(self, bg=p["bg"], padx=10)
        table_frame.pack(fill="both", expand=True, pady=4)

        cols = ("min", "max", "gpa", "grade", "label")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                 show="headings", selectmode="browse")
        self.tree.heading("min",   text="Min Marks")
        self.tree.heading("max",   text="Max Marks")
        self.tree.heading("gpa",   text="GPA Value")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("label", text="Description")

        self.tree.column("min",   width=95,  anchor="center")
        self.tree.column("max",   width=95,  anchor="center")
        self.tree.column("gpa",   width=95,  anchor="center")
        self.tree.column("grade", width=80,  anchor="center")
        self.tree.column("label", width=280, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._edit_selected())
        self._tag_rows()

        # ── Bottom bar ───────────────────────────────────
        bottom = tk.Frame(self, bg=p["surface"], pady=10, padx=14)
        bottom.pack(fill="x", side="bottom")

        tk.Button(bottom, text="✔  Save & Apply",
                  bg=p["accent"], fg=p["on_accent"],
                  activebackground=p["accent_hover"],
                  activeforeground=p["on_accent"],
                  font=("Segoe UI", 11, "bold"),
                  relief="flat", cursor="hand2",
                  padx=18, pady=8,
                  command=self._save_apply).pack(side="right", padx=6)
        tk.Button(bottom, text="Cancel",
                  bg=p["surface2"], fg=p["fg"],
                  activebackground=p["surface"],
                  activeforeground=p["fg"],
                  font=("Segoe UI", 10),
                  relief="flat", cursor="hand2",
                  padx=14, pady=8,
                  command=self.destroy).pack(side="right", padx=4)

        self.info_lbl = tk.Label(bottom,
                                 text="Double-click a row to edit it.",
                                 bg=p["surface"], fg=p["fg_muted"],
                                 font=("Segoe UI", 9))
        self.info_lbl.pack(side="left")

    def _tag_rows(self):
        p = self.app.palette
        self.tree.tag_configure("odd",  background=p["surface"])
        self.tree.tag_configure("even", background=p["row_alt"])

    def _load_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        from core.gpa_scale import grade_letter
        for idx, (lo, hi, gpa, lbl) in enumerate(self._rows):
            tag = "odd" if idx % 2 == 0 else "even"
            self.tree.insert("", "end",
                             values=(lo, hi, f"{gpa:.1f}",
                                     grade_letter(gpa), lbl),
                             tags=(tag,))

    def _load_preset(self, *_):
        name = self.preset_var.get()
        rows = PRESET_SCALES.get(name)
        if rows:
            if messagebox.askyesno("Load Preset",
                                   f"Replace current scale with '{name}'?",
                                   parent=self):
                self._rows = list(rows)
                self._load_table()
                self.info_lbl.config(text=f"Preset '{name}' loaded.")

    def _add_row(self):
        _RowDialog(self, self.app, None, self._on_row_saved)

    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Edit Row", "Select a row first.", parent=self)
            return
        idx = self.tree.index(sel[0])
        _RowDialog(self, self.app, self._rows[idx], self._on_row_saved, idx)

    def _on_row_saved(self, row, index=None):
        if index is None:
            self._rows.append(row)
        else:
            self._rows[index] = row
        # re-sort by min marks descending
        self._rows.sort(key=lambda r: r[0], reverse=True)
        self._load_table()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a row first.", parent=self)
            return
        idx = self.tree.index(sel[0])
        row = self._rows[idx]
        if messagebox.askyesno("Delete Row",
                               f"Delete row: {row[3]}?", parent=self):
            self._rows.pop(idx)
            self._load_table()

    def _reset_default(self):
        if messagebox.askyesno("Reset Scale",
                               "Reset to the default 85→4.0 scale?",
                               parent=self):
            self._rows = list(DEFAULT_SCALE_ROWS)
            self._load_table()
            self.info_lbl.config(text="Reset to default scale.")

    def _save_apply(self):
        if not self._rows:
            messagebox.showerror("Save", "Scale cannot be empty.", parent=self)
            return
        self.app.scale = list(self._rows)
        save_scale(self._rows)
        self.app.on_scale_changed()
        self.info_lbl.config(text="✔ Scale saved and applied to all tabs.")
        messagebox.showinfo("Saved",
                            "GPA Scale saved and applied!\n"
                            "All calculations now use the new scale.",
                            parent=self)
        self.destroy()


class _RowDialog(tk.Toplevel):
    """Small dialog to add/edit a single scale row."""
    def __init__(self, parent, app, existing_row, callback, index=None):
        super().__init__(parent)
        self.app = app
        self.callback = callback
        self.index = index
        self.title("Edit Scale Row" if existing_row else "Add Scale Row")
        self.geometry("360x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build(existing_row)

    def _build(self, row):
        p = self.app.palette
        self.configure(bg=p["bg"])
        pad = dict(padx=16, pady=6)

        def lbl(text):
            tk.Label(self, text=text, bg=p["bg"], fg=p["fg"],
                     font=("Segoe UI", 10)).pack(anchor="w", **pad)

        def entry(default=""):
            e = ttk.Entry(self, width=18)
            e.insert(0, str(default))
            e.pack(anchor="w", padx=16, pady=2)
            return e

        lbl("Min Marks (e.g. 80):")
        self.e_min = entry(row[0] if row else "")

        lbl("Max Marks (e.g. 84):")
        self.e_max = entry(row[1] if row else "")

        lbl("GPA Value (e.g. 3.7):")
        self.e_gpa = entry(f"{row[2]:.1f}" if row else "")

        btn_frame = tk.Frame(self, bg=p["bg"])
        btn_frame.pack(fill="x", padx=16, pady=12)
        tk.Button(btn_frame, text="Save",
                  bg=p["accent"], fg=p["on_accent"],
                  activebackground=p["accent_hover"],
                  activeforeground=p["on_accent"],
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=14, pady=6,
                  command=self._save).pack(side="right", padx=4)
        tk.Button(btn_frame, text="Cancel",
                  bg=p["surface2"], fg=p["fg"],
                  activebackground=p["surface"],
                  activeforeground=p["fg"],
                  relief="flat", padx=12, pady=6,
                  command=self.destroy).pack(side="right")

    def _save(self):
        try:
            lo  = int(self.e_min.get().strip())
            hi  = int(self.e_max.get().strip())
            gpa = float(self.e_gpa.get().strip())
            if lo < 0 or hi > 100 or lo > hi:
                raise ValueError("Min must be ≤ Max, both in 0–100.")
            if not (0.0 <= gpa <= 4.0):
                raise ValueError("GPA must be between 0.0 and 4.0.")
        except ValueError as err:
            messagebox.showerror("Validation", str(err), parent=self)
            return
        label = build_label(lo, hi, gpa)
        self.callback((lo, hi, gpa, label), self.index)
        self.destroy()
