from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics, QKeyEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from logic import CalculatorLogic


class QtCalculator(QMainWindow):

    def __init__(self):
        super().__init__()
        self.logic = CalculatorLogic()
        self.current_theme = "light"
        self.clipboard = QApplication.clipboard()

        self.setWindowTitle("Kalkulator")
        self.setMinimumSize(340, 580)
        self.resize(360, 600)

        self.init_ui()
        self.apply_theme("light")
        self.update_display()
        self.update_history()
        self._sync_display_limit()

    def init_ui(self):

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._build_top_menu()
        self._build_history_area()
        self._build_display_area()
        self._build_button_grid()

    def _build_top_menu(self):

        self.top_menu = QWidget()
        self.top_menu.setObjectName("topMenu")
        self.top_menu.setFixedHeight(38)
        menu_layout = QHBoxLayout(self.top_menu)
        menu_layout.setContentsMargins(18, 0, 18, 0)
        menu_layout.setSpacing(20)

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("menuBtn")
        self.settings_button.setText("Ustawienia")
        self.settings_menu = QMenu(self)
        self.settings_button.clicked.connect(self.show_settings_menu)
        self.settings_menu.aboutToHide.connect(lambda: self.settings_button.setText("Ustawienia"))
        self._create_settings_menu()

        self.about_button = QPushButton("Opis")
        self.about_button.setObjectName("menuBtnActive")
        self.about_button.clicked.connect(self.show_about)

        menu_layout.addWidget(self.settings_button)
        menu_layout.addWidget(self.about_button)
        menu_layout.addStretch()
        self.main_layout.addWidget(self.top_menu)

    def _create_settings_menu(self):

        self.settings_menu.clear()
        self.settings_menu.addAction("🌓 Motyw: Jasny", lambda: self.apply_theme("light"))
        self.settings_menu.addAction("🥝 Motyw: Kiwi", lambda: self.apply_theme("kiwi"))
        self.settings_menu.addSeparator()
        pin_action = self.settings_menu.addAction("📌 Zawsze na wierzchu")
        pin_action.setCheckable(True)
        pin_action.toggled.connect(self.toggle_always_on_top)
        self.settings_menu.addAction("🧹 Wyczyść historię", self.clear_history)

    def show_settings_menu(self):

        self.settings_button.setText("Ustawienia ▾")
        menu_pos = self.settings_button.mapToGlobal(self.settings_button.rect().bottomLeft())
        self.settings_menu.popup(menu_pos)

    def _build_history_area(self):
        self.history_display = QListWidget()
        self.history_display.setObjectName("historyDisplay")
        self.history_display.setFixedHeight(95)
        self.history_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.history_display)

        self.divider = QFrame()
        self.divider.setObjectName("divider")
        self.divider.setFixedHeight(1)
        self.main_layout.addWidget(self.divider)

    def _build_display_area(self):

        self.hint_label = QLabel("")
        self.hint_label.setObjectName("copyHint")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addWidget(self.hint_label)

        self.display = QLabel("0")
        self.display.setObjectName("mainDisplay")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.display.setWordWrap(True)
        self.display.setFixedHeight(96)
        self.main_layout.addWidget(self.display)

    def _build_button_grid(self):

        self.grid_container = QWidget()
        self.grid_container.setObjectName("gridContainer")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(1)

        buttons = [
            ("C", 0, 0, "btn_c"),
            ("xʸ", 0, 1, "btn_op"),
            ("√", 0, 2, "btn_op"),
            ("÷", 0, 3, "btn_op"),
            ("7", 1, 0, ""),
            ("8", 1, 1, ""),
            ("9", 1, 2, ""),
            ("×", 1, 3, "btn_op"),
            ("4", 2, 0, ""),
            ("5", 2, 1, ""),
            ("6", 2, 2, ""),
            ("−", 2, 3, "btn_op"),
            ("1", 3, 0, ""),
            ("2", 3, 1, ""),
            ("3", 3, 2, ""),
            ("+", 3, 3, "btn_op"),
            ("0", 4, 0, ""),
            (".", 4, 1, ""),
            ("=", 4, 2, "btn_eq", 2),
        ]

        for entry in buttons:
            text, row, col, obj_name = entry[:4]
            span = entry[4] if len(entry) == 5 else 1
            btn = QPushButton(text)
            btn.setObjectName(obj_name if obj_name else "btn_num")
            btn.setFixedHeight(60)
            btn.clicked.connect(self.on_click)
            self.grid_layout.addWidget(btn, row, col, 1, span)

        self.main_layout.addWidget(self.grid_container)

    def on_click(self):
        text = self.sender().text()
        if text == "C":
            self.logic.clear_all()
            self.hint_label.setText("")
            self.update_display()
            return

        if text == "=":
            self.handle_eval()
            return

        symbol = "^" if text == "xʸ" else text
        self._sync_display_limit()
        self.logic.add_character(symbol)
        if self.logic.consume_input_limited():
            self.hint_label.setText(">>> LIMIT ZNAKOW" if self.current_theme == "kiwi" else "Limit znakow")
        else:
            self.hint_label.setText("")
        self.update_display()
        if text == "√":
            self.update_history()

    def handle_eval(self):
        result = self.logic.evaluate()
        self.update_display()
        self.update_history()
        if result.startswith("Błąd"):
            self.hint_label.setText("")
            return

        self.hint_label.setText("")

    def update_display(self):
        self._sync_display_limit()
        text = self.logic.current_expression
        self.display.setText(self._format_display_text(text))
        has_error = text.startswith("Błąd")
        self.display.setProperty("errorState", "true" if has_error else "false")
        self.display.style().unpolish(self.display)
        self.display.style().polish(self.display)

    def update_history(self):
        self.history_display.clear()
        prefix = ">>> " if self.current_theme == "kiwi" else ""
        for entry in self.logic.get_history():
            item = QListWidgetItem(f"{prefix}{entry}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.history_display.addItem(item)
        self.history_display.scrollToBottom()

    def apply_theme(self, theme):

        self.current_theme = theme
        self.setWindowTitle("Kalkulator [Tryb Kiwi]" if theme == "kiwi" else "Kalkulator")

        if theme == "kiwi":
            self.grid_layout.setSpacing(6)
            self.grid_layout.setContentsMargins(12, 12, 12, 12)
            style = """
                QMainWindow, QWidget#root { background: #0d0e0d; border: none; }
                QWidget#topMenu { background: #1a1b1a; border-bottom: 1px solid #2d2e2d; }
                QPushButton#menuBtn { background: transparent; color: #aab8ab; border: none; font-size: 13px; text-align: left; padding: 4px 6px; border-radius: 6px; }
                QPushButton#menuBtn:hover { background: #242524; color: #cfe4d1; }
                QPushButton#menuBtnActive { background: transparent; color: #84cc16; border: none; font-size: 13px; font-weight: 700; text-align: left; padding: 4px 6px; border-radius: 6px; }
                QPushButton#menuBtnActive:hover { background: #273027; color: #a3e635; }
                QMenu { background: #121312; color: #d1d5db; border: 1px solid #2d2e2d; padding: 4px; }
                QMenu::item:selected { background: #1f2937; color: #84cc16; }
                QListWidget#historyDisplay { background: #0a0b0a; color: #84cc16; border: none; padding: 15px 20px 5px 20px; font-size: 13px; font-family: "Consolas"; }
                QFrame#divider { background: #2d2e2d; }
                QLabel#copyHint { background: #0a0b0a; color: #84cc16; opacity: 0.7; font-size: 10px; font-weight: 600; padding-right: 20px; min-height: 15px; }
                QLabel#mainDisplay { background: #0a0b0a; color: #ecfccb; font-size: 46px; font-family: "Consolas"; padding: 10px 20px 20px 20px; }
                QLabel#mainDisplay[errorState="true"] { color: #f87171; font-size: 24px; font-weight: 600; }
                QWidget#gridContainer { background: #0d0e0d; }
                QPushButton { background: #181918; color: #cbd5e1; border: none; border-radius: 8px; font-size: 20px; font-family: "Consolas"; }
                QPushButton:hover { background: #222422; }
                QPushButton#btn_op { color: #84cc16; }
                QPushButton#btn_op:hover { background: #273027; color: #a3e635; }
                QPushButton#btn_eq { background: #84cc16; color: #0d0e0d; font-weight: 700; }
                QPushButton#btn_eq:hover { background: #a3e635; }
                QPushButton#btn_c { color: #f87171; }
                QPushButton#btn_c:hover { background: #3a1f25; color: #fca5a5; }
            """
        else:
            self.grid_layout.setSpacing(1)
            self.grid_layout.setContentsMargins(0, 0, 0, 0)
            style = """
                QMainWindow, QWidget#root { background: #ffffff; border: none; }
                QWidget#topMenu { background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
                QPushButton#menuBtn { background: transparent; color: #334155; border: none; font-size: 13px; text-align: left; padding: 4px 6px; border-radius: 6px; }
                QPushButton#menuBtn:hover { background: #e2e8f0; color: #0f172a; }
                QPushButton#menuBtnActive { background: transparent; color: #0067c0; border: none; font-size: 13px; font-weight: 700; text-align: left; padding: 4px 6px; border-radius: 6px; }
                QPushButton#menuBtnActive:hover { background: #dbeafe; color: #0057a8; }
                QMenu { background: #ffffff; color: #333333; border: 1px solid #dddddd; padding: 5px 0; }
                QMenu::item:selected { background: #f0f7ff; color: #0067c0; }
                QListWidget#historyDisplay { background: #ffffff; color: #64748b; border: none; padding: 15px 20px 5px 20px; font-size: 13px; }
                QFrame#divider { background: rgba(0, 0, 0, 0.08); margin-left: 20px; margin-right: 20px; }
                QLabel#copyHint { color: #0067c0; font-size: 10px; font-weight: 600; padding-right: 20px; min-height: 15px; }
                QLabel#mainDisplay { background: #ffffff; color: #1e293b; font-size: 46px; padding: 10px 20px 20px 20px; }
                QLabel#mainDisplay[errorState="true"] { color: #e11d48; font-size: 24px; font-weight: 600; }
                QWidget#gridContainer { background: #eeeeee; }
                QPushButton { background: #ffffff; color: #333333; border: none; font-size: 20px; }
                QPushButton:hover { background: #f1f5f9; }
                QPushButton#btn_op { color: #0067c0; font-weight: 600; }
                QPushButton#btn_op:hover { background: #e0f2fe; color: #0369a1; }
                QPushButton#btn_eq { background: #0067c0; color: #ffffff; font-weight: 600; }
                QPushButton#btn_eq:hover { background: #0b79d0; }
                QPushButton#btn_c { color: #e11d48; }
                QPushButton#btn_c:hover { background: #fee2e2; color: #be123c; }
            """

        self.setStyleSheet(style)
        self.update_history()

    def clear_history(self):
        self.logic.clear_history()
        self.update_history()

    def toggle_always_on_top(self, enabled):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
        self.show()

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            self.clipboard.setText(self.display.text())
            if self.current_theme == "kiwi":
                self.hint_label.setText(">>> SCHOWEK: ZSYNCHRONIZOWANY")
            else:
                self.hint_label.setText("Wynik skopiowany: Ctrl+C")
            return

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            self._sync_display_limit()
            self.logic.add_character(self.clipboard.text())
            if self.logic.consume_input_limited():
                self.hint_label.setText(">>> LIMIT ZNAKOW" if self.current_theme == "kiwi" else "Limit znakow")
            else:
                self.hint_label.setText("")
            self.update_display()
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_eval()
            return

        if event.key() == Qt.Key.Key_Backspace:
            self.logic.backspace()
            self.hint_label.setText("")
            self.update_display()
            return

        if event.key() == Qt.Key.Key_Escape:
            self.logic.clear_all()
            self.hint_label.setText("")
            self.update_display()
            return

        text = event.text()
        if text == "=":
            self.handle_eval()
            return

        if text and text in "0123456789.+-*/^":
            self._sync_display_limit()
            self.logic.add_character(text)
            if self.logic.consume_input_limited():
                self.hint_label.setText(">>> LIMIT ZNAKOW" if self.current_theme == "kiwi" else "Limit znakow")
            else:
                self.hint_label.setText("")
            self.update_display()
            return

        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent):

        super().resizeEvent(event)
        # Po resize natychmiast aktualizujemy limit i render tekstu.
        self._sync_display_limit()
        self.update_display()

    def _sync_display_limit(self):

        font_metrics = QFontMetrics(self.display.font())
        available_px = max(120, self.display.width() - 40)
        char_px = max(1, font_metrics.horizontalAdvance("8"))
        line_capacity = max(6, available_px // char_px)
        # Utrzymujemy bufor na dwie linie.
        dynamic_limit = max(12, line_capacity * 2)
        self.logic.set_max_expression_length(dynamic_limit)

    def _format_display_text(self, text):

        if not text:
            return "0"
        if text.startswith("Błąd"):
            return text

        font_metrics = QFontMetrics(self.display.font())
        available_px = max(120, self.display.width() - 40)
        char_px = max(1, font_metrics.horizontalAdvance("8"))
        line_capacity = max(6, available_px // char_px)
        if len(text) <= line_capacity:
            return text

        chunks = []
        for start in range(0, len(text), line_capacity):
            chunks.append(text[start: start + line_capacity])
        return "\n".join(chunks[-2:])

    def show_about(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("Opis")
        dialog.setModal(True)
        dialog.setFixedSize(460, 300)

        root_layout = QVBoxLayout(dialog)
        root_layout.setContentsMargins(16, 16, 16, 16)

        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 18)
        card_layout.setSpacing(10)

        title = QLabel("Kalkulator")
        version = QLabel("Wersja 1.0.0")
        desc = QLabel("Aplikacja desktopowa wspierająca dynamiczne motywy i historię sesji.")
        desc.setWordWrap(True)

        shortcuts = QLabel(
            "<b>Skróty:</b> [Enter] Wynik &nbsp;&nbsp; [Ctrl+C] Kopiuj &nbsp;&nbsp; [Ctrl+V] Wklej &nbsp;&nbsp; [Esc] Czyść"
        )
        shortcuts.setWordWrap(True)

        author = QLabel("Autor: <b>Piotr Zienowicz</b><br/>Nr indeksu: <b>212032</b>")
        close_btn = QPushButton("ZAMKNIJ")
        close_btn.clicked.connect(dialog.accept)

        title.setObjectName("aboutTitle")
        version.setObjectName("aboutVersion")
        desc.setObjectName("aboutText")
        shortcuts.setObjectName("aboutShortcuts")
        author.setObjectName("aboutAuthor")
        close_btn.setObjectName("aboutCloseBtn")

        card_layout.addWidget(title)
        card_layout.addWidget(version)
        card_layout.addWidget(desc)
        card_layout.addWidget(shortcuts)
        card_layout.addWidget(author)
        card_layout.addStretch()
        card_layout.addWidget(close_btn)

        root_layout.addWidget(card)

        if self.current_theme == "kiwi":
            dialog.setStyleSheet(
                """
                QDialog { background: #101116; }
                QWidget { background: #1e293b; border: 1px solid #84cc16; border-radius: 20px; }
                QLabel { color: #ffffff; background: transparent; border: none; }
                QLabel#aboutTitle { color: #84cc16; font-size: 26px; font-weight: 700; }
                QLabel#aboutVersion { color: #94a3b8; font-size: 13px; }
                QLabel#aboutText { font-size: 13px; }
                QLabel#aboutAuthor { font-size: 13px; }
                QLabel#aboutShortcuts { background: rgba(0, 0, 0, 0.25); border-radius: 12px; padding: 12px; font-size: 12px; }
                QPushButton#aboutCloseBtn { height: 40px; background: #84cc16; color: #0d0e0d; border: none; border-radius: 8px; font-weight: 700; }
                QPushButton#aboutCloseBtn:hover { background: #a3e635; }
                """
            )
        else:
            dialog.setStyleSheet(
                """
                QDialog { background: #f1f5f9; }
                QWidget { background: #ffffff; border: 1px solid #0067c0; border-radius: 20px; }
                QLabel { color: #1e293b; background: transparent; border: none; }
                QLabel#aboutTitle { color: #0067c0; font-size: 26px; font-weight: 700; }
                QLabel#aboutVersion { color: #64748b; font-size: 13px; }
                QLabel#aboutText { font-size: 13px; }
                QLabel#aboutAuthor { font-size: 13px; }
                QLabel#aboutShortcuts { background: #e6f0fb; color: #1e3a5f; border-radius: 12px; padding: 12px; font-size: 12px; }
                QPushButton#aboutCloseBtn { height: 40px; background: #0067c0; color: #ffffff; border: none; border-radius: 8px; font-weight: 700; }
                QPushButton#aboutCloseBtn:hover { background: #0b79d0; }
                """
            )
        dialog.exec()
