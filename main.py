#!/usr/bin/env python3
"""
Linux Desktop Chat – Standard-Startpunkt.

Delegiert an run_gui_shell (kanonische GUI-Implementierung).

Start:
    python main.py
    python run_gui_shell.py     # Direkt
    python -m app               # Modul-Start (empfohlen)

Legacy-GUI (deprecated):
    python archive/run_legacy_gui.py
"""

from run_gui_shell import main

if __name__ == "__main__":
    main()
