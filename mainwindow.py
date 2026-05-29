import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from controllers.screen1 import Screen1Controller
from controllers.screen2 import Screen2Controller


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        loader = QUiLoader()
        ui_file = QFile("/home/htic/MLN/ANU-DV/designer/mainwindow.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()
        self.setCentralWidget(self.ui.centralwidget)

        self.ui.stackedWidget.setCurrentIndex(0)
        # self.ui.stackedWidget.setCurrentIndex(1)

        self.screen1_controller = Screen1Controller(self.ui)
        self.screen2_controller = Screen2Controller(self.ui)


        self.screen1_controller.from_s1_to_s2.connect(self.goto_screen2)

    # ============================================
    # SCREEN SWITCH
    # ============================================
    def goto_screen2(self):
 
        self.ui.stackedWidget.setCurrentIndex(1)
 

app = QApplication(sys.argv)
window = MainWindow()
window.resize(1200, 800)
window.show()
sys.exit(app.exec())
