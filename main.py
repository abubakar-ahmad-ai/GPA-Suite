"""
main.py
-------
Entry point for Professional GPA Suite.
Run:  python main.py
"""

import sys
import os

# Ensure project root is on sys.path when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import ProApp


def main():
    app = ProApp()
    app.mainloop()


if __name__ == "__main__":
    main()
