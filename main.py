import sys
import re
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QFrame
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt


# --- symbol map ---
symbol_map = {
    "prime": r"'", "sqrt": r"\\sqrt", "->": r"\\to", "<-": r"\\leftarrow",
    "inf": r"\\infty", "sum": r"\\sum", "int": r"\\int",
    "alpha": r"\\alpha", "beta": r"\\beta", "theta": r"\\theta",
    "neq": r"\\neq", "leq": r"\\leq", "geq": r"\\geq", "pi": r"\\pi"
}


def tokenize_and_replace(expr: str, symbol_map: dict) -> str:
    for key, latex in sorted(symbol_map.items(), key=lambda kv: -len(kv[0])):
        pattern = r'\b' + re.escape(key) + r'\b'
        expr = re.sub(pattern, latex, expr)

    expr = re.sub(r'\\sqrt\s*\(\s*([^\)]+)\s*\)', r'\\sqrt{\1}', expr)
    expr = re.sub(r'\\sqrt\s+([A-Za-z0-9\{\}\\]+)', r'\\sqrt{\1}', expr)
    return expr.strip()


def render_formula_to_png(formula: str, out_path: str, fontsize=36, dpi=200):
    latex_expr = tokenize_and_replace(formula, symbol_map)
    mathtext = f"${latex_expr}$"

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, mathtext, fontsize=fontsize)
    plt.axis("off")
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight", pad_inches=0.05, transparent=True)
    plt.close(fig)


# --- main GUI ---
class MathWriter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MATH")
        self.setGeometry(200, 200, 600, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #f6f6f6;
                color: #202020;
                font-size: 14px;
                font-family: "Segoe UI";
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #e8e8e8;
                color: #000;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
            }
        """)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        label = QLabel("CILCK")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(label)

        self.input_box = QLineEdit()
        self.input_box.textChanged.connect(self.update_preview)
        main_layout.addWidget(self.input_box)
        button_layout = QHBoxLayout()
        symbols = ["sqrt()", "pi", "alpha", "beta", "theta", "sum", "int", "->", "<-", "inf", "prime"]
        for sym in symbols:
            btn = QPushButton(sym)
            btn.clicked.connect(lambda _, s=sym: self.insert_symbol(s))
            button_layout.addWidget(btn)
        main_layout.addLayout(button_layout)

        self.preview_label = QLabel("OUTPUT")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedHeight(250) # FIXIT ON HEIGHT
        self.preview_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.preview_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        main_layout.addWidget(self.preview_label)

        # --- Save Button ---
        self.save_button = QPushButton("SAVE")
        self.save_button.clicked.connect(self.save_formula)
        main_layout.addWidget(self.save_button)

        self.update_preview()

    def insert_symbol(self, symbol):
        cursor_pos = self.input_box.cursorPosition()
        text = self.input_box.text()
        new_text = text[:cursor_pos] + symbol + text[cursor_pos:]
        self.input_box.setText(new_text)
        self.input_box.setCursorPosition(cursor_pos + len(symbol))

    def update_preview(self):
        text = self.input_box.text()
        if not text.strip():
            self.preview_label.setText("TYPE:")
            return
        try:
            render_formula_to_png(text, "preview.png", fontsize=28, dpi=200)
            pixmap = QPixmap("preview.png")
            scaled = pixmap.scaled(
                self.preview_label.width() - 20,
                self.preview_label.height() - 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
        except Exception as e:
            self.preview_label.setText(f"ERROR {e}")

    def save_formula(self):
        text = self.input_box.text()
        if not text.strip():
            self.preview_label.setText("TYPE MATH")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "SAVE", "", "PNG Files (*.png)")
        if file_path:
            try:
                render_formula_to_png(text, file_path, fontsize=42, dpi=300)
                self.preview_label.setText(f"OK \n{file_path}")
            except Exception as e:
                self.preview_label.setText(f"ERROR {e}")


# RUN PROGRAM
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme("accessories-calculator"))
    window = MathWriter()
    window.show()
    sys.exit(app.exec())

