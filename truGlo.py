import sys
import os
import json
from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtCore import Qt, QPoint
from pynput import keyboard
import threading

MAPPING_FILE = "keymap.json"

DEFAULT_BINDINGS = {
    "q": "sb rt", "w": "sb thru", "e": "sb lt", "r": "sb ped",
    "a": "wb rt", "s": "wb thru", "d": "wb lt", "f": "wb ped",
    "z": "nb rt", "x": "nb thru", "c": "nb lt", "v": "nb ped",
    "1": "eb rt", "2": "eb thru", "3": "eb lt", "4": "eb ped",
    "5": "save", "6": "next", "7": "bucket 3", "8": "bucket 4",
    "m": "menu", "b": "bike", "h": "heavy", "del": "delete"
}

class FloatingButton(QWidget):
    def __init__(self, key, label):
        super().__init__()
        self.key = key
        self.label = label
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.button = QPushButton(label, self)
        self.base_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                font-weight: bold;
                border: 2px solid white;
                padding: 10px;
            }
        """
        self.highlight_style = """
            QPushButton {
                background-color: lime;
                color: black;
                font-weight: bold;
                border: 2px solid white;
                padding: 10px;
            }
        """
        self.button.setStyleSheet(self.base_style)
        self.button.resize(self.button.sizeHint())
        self.resize(self.button.size())

        self.drag_offset = None

        self.button.mousePressEvent = self.mousePressEvent
        self.button.mouseMoveEvent = self.mouseMoveEvent
        self.button.mouseReleaseEvent = self.mouseReleaseEvent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.drag_offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            if self.drag_offset:
                new_pos = event.globalPosition().toPoint() - self.drag_offset
                self.move(new_pos)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None

    def highlight(self):
        self.button.setStyleSheet(self.highlight_style)

    def unhighlight(self):
        self.button.setStyleSheet(self.base_style)

def load_keymap():
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("warning: invalid json. using default mappings.")
    return DEFAULT_BINDINGS

def start_key_listener(buttons_by_key):
    def on_press(key):
        k = key.char.lower() if hasattr(key, 'char') and key.char else str(key).replace("Key.", "")
        if k in buttons_by_key:
            buttons_by_key[k].highlight()

    def on_release(key):
        k = key.char.lower() if hasattr(key, 'char') and key.char else str(key).replace("Key.", "")
        if k in buttons_by_key:
            buttons_by_key[k].unhighlight()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

def main():
    app = QApplication(sys.argv)

    keymap = load_keymap()
    buttons_by_key = {}

    for idx, (key, label) in enumerate(keymap.items()):
        btn = FloatingButton(key, label)
        btn.move(100 + (idx % 5) * 120, 100 + (idx // 5) * 80)
        btn.show()
        buttons_by_key[key] = btn

    threading.Thread(target=start_key_listener, args=(buttons_by_key,), daemon=True).start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
