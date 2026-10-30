"""
Automated headless GUI verification for main.py
"""

import os
import sys
import tkinter as tk

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from main import ImageProcessingToolkitApp

def test_gui_initialization():
    print("Testing GUI initialization...")
    root = tk.Tk()
    root.withdraw()  # Offscreen
    app = ImageProcessingToolkitApp(root)
    print("[PASS] ImageProcessingToolkitApp initialized successfully")

    # Test loading sample image
    sample_path = os.path.join("samples", "sample_landscape.jpg")
    if os.path.exists(sample_path):
        app._load_image_from_path(sample_path)
        assert app.original_image is not None
        assert app.processed_image is not None
        print("[PASS] Sample image loaded into GUI state")

        # Test triggering a filter
        app.apply_instant_filter("Grayscale", lambda img: img)
        assert len(app.undo_stack) == 1
        print("[PASS] Filter triggered & undo stack pushed")

        # Test Undo
        app.on_undo()
        assert len(app.undo_stack) == 0
        assert len(app.redo_stack) == 1
        print("[PASS] Undo operation succeeded")

        # Test Redo
        app.on_redo()
        assert len(app.undo_stack) == 1
        print("[PASS] Redo operation succeeded")

    root.destroy()
    print("\nALL GUI VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_gui_initialization()
