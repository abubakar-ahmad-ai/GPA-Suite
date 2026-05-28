# 🎓 Professional GPA Suite

A feature-rich GPA Calculator desktop application built with Python & Tkinter.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📸 Screenshots

### 1. Single Semester Calculator

![Single Semester](screenshots/1_Single_Semester.PNG)

### 2. Semesters by SGPA

![Semesters by SGPA](screenshots/2_Semesters_by_SGPA.PNG)

### 3. Multi-Semester CGPA

![Multi Semester](screenshots/3_Multi_Semesters.PNG)

### 4. Target CGPA Planner

![Target Planner](screenshots/4_Target.PNG)

### 5. GPA Scale Editor

![GPA Scale](screenshots/5_GPA_Scale.PNG)

---

## ✨ Features

- 📊 **Single Semester** — Enter subjects, marks, credit hours → auto GPA
- 📈 **Semesters by SGPA** — Enter SGPA per semester → Cumulative CGPA
- 🗂️ **Multi-Semester** — Full subject-level detail across all semesters
- 🎯 **Target CGPA Planner** — Find required GPA to reach your goal
- ⚙️ **GPA Scale Editor** — Customize grading scale with presets
- 🌙 **3 Themes** — Light, Dark, Blue
- 💾 **CSV Import/Export** — Save and load your data

---

## 🚀 How to Run

### Requirements

- Python 3.8 or higher

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/abubakar-ahmad-ai/GPA-Suite.git

# 2. Go into the folder
cd GPA-Suite

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

---

## 📁 Project Structure

GPA-Suite/
├── main.py # Entry point
├── core/
│ ├── calculator.py # GPA logic
│ └── gpa_scale.py # Scale management
├── ui/
│ ├── app.py # Main window
│ ├── tabs/ # All 4 tabs
│ ├── widgets/ # Scale editor, semester panel
│ └── theme_manager.py # Theme switching
├── screenshots/ # App screenshots
├── requirements.txt
└── README.md

---

## 👨‍💻 Author

**Abubakar Ahmad**  
GitHub: [@abubakar-ahmad-ai](https://github.com/abubakar-ahmad-ai)
