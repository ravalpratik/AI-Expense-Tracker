"""Page module imports for the AI Expense Tracker app."""

import importlib.util
import os

_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_module(name: str, filename: str):
    """Load a page module from the pages directory."""
    path = os.path.join(_PAGES_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dashboard = _load_module("dashboard", "1_Dashboard.py")
add_expense = _load_module("add_expense", "2_Add_Expense.py")
ocr_scanner = _load_module("ocr_scanner", "3_OCR_Bill_Scanner.py")
predictions = _load_module("predictions", "4_Predictions.py")
analytics = _load_module("analytics", "5_Analytics.py")
profile = _load_module("profile", "6_Profile.py")
