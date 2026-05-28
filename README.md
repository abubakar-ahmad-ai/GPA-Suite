# 📊 Professional GPA Suite

A feature-rich, multi-mode GPA calculator built with Python and Tkinter — no external libraries required.

---

## ✨ Features

| Feature                     | Description                                             |
| --------------------------- | ------------------------------------------------------- |
| **Single Semester**         | Enter subjects, marks, credit hours → instant SGPA      |
| **Semesters by SGPA**       | Enter each semester's SGPA + credits → cumulative CGPA  |
| **Multi-Semester Detailed** | Full subject tables per semester, save/load as JSON     |
| **Target CGPA Planner**     | Enter your goal CGPA → get 4 strategy plans             |
| **GPA Scale Editor**        | Edit the marks→GPA scale from the GUI — no code needed! |
| **3 Themes**                | Light, Dark, and Blue-Dark modes                        |
| **CSV Import/Export**       | Open and save semester data as CSV                      |
| **Project Save/Load**       | Multi-semester projects saved as JSON                   |

---

## 🚀 How to Run

```bash
# Make sure Python 3.9+ is installed
python main.py
```

No pip install needed — everything uses Python's built-in libraries.

---

## 📁 Project Structure

```
GPA-Suite/
├── main.py                    # Entry point
├── requirements.txt
├── README.md
├── .gitignore
│
├── core/
│   ├── gpa_scale.py           # GPA scale logic + save/load
│   └── calculator.py          # SGPA, CGPA, planner strategies
│
├── ui/
│   ├── theme.py               # Colors, fonts, ttk styles
│   ├── app.py                 # Main window
│   ├── tabs/
│   │   ├── single_semester.py
│   │   ├── sgpa_only.py
│   │   ├── multi_semester.py
│   │   └── target_planner.py
│   └── widgets/
│       ├── scale_editor.py    # GUI-based GPA scale editor
│       └── semester_panel.py  # Reusable semester panel
│
└── data/
    └── custom_scale.json      # Saved custom scale (auto-created)
```

---

## ⚖️ GPA Scale

Default scale uses **85 → 4.0** (common in Pakistani universities).

You can change the scale at any time from the **GPA Scale** button in the toolbar — supports any university's grading system (80→4.0, 90→4.0, etc.).

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action                      |
| -------- | --------------------------- |
| `F5`     | Recalculate Single Semester |
| `Ctrl+S` | Save CSV                    |
| `Ctrl+O` | Open CSV                    |
| `Ctrl+E` | Open GPA Scale Editor       |
| `Ctrl+D` | Cycle Theme                 |

---

## 👨‍💻 Author

Made with ❤️ as a Python learning project.

---

## 📄 License

MIT License — free to use and modify.
