import sys
import os


def start_qt():
    from PyQt6.QtWidgets import QApplication
    from view_qt import QtCalculator
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QtCalculator()
    win.show()
    sys.exit(app.exec())


def start_gtk():
    from view_gtk import GtkApp
    app = GtkApp()
    app.run(sys.argv)


if __name__ == "__main__":
    print("Wybierz wersję: [1] Qt6 (Windows), [2] GTK4 (Linux/MSYS)")
    wybor = input("Wybór: ")

    if wybor == "1":
        start_qt()
    elif wybor == "2":
        start_gtk()
    else:
        print("Nieprawidłowy wybór.")
