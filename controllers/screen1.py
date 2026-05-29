from PySide6.QtCore import QObject, Signal


class Screen1Controller(QObject):

    from_s1_to_s2 = Signal()

    def __init__(self, ui):

        super().__init__()

        self.ui = ui

        self.ui.btn_to_screen2.clicked.connect(self.go_to_screen2)

    # ============================================
    # GO TO SCREEN 2
    # ============================================
    def go_to_screen2(self):

        self.from_s1_to_s2.emit()