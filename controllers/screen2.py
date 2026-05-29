import shutil
from pathlib import Path

from PySide6.QtCore import QObject, QDate, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QListView,
    QTreeView,
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QFrame,
)


from config import Config


class Screen2Controller(QObject):

    def __init__(self, ui):

        super().__init__()

        self.ui = ui

        self.selected_folders = []

        # ----------------------------------------
        # DEFAULT SETUP
        # ----------------------------------------
        self.load_default_centers()

        self.ui.date_choose_btn.setDate(
            QDate.currentDate()
        )

        # ----------------------------------------
        # CONNECT BUTTONS
        # ----------------------------------------
        self.ui.center_add_btn.clicked.connect(
            self.add_new_center
        )

        self.ui.folder_choose_btn.clicked.connect(
            self.select_folders
        )

        self.ui.upload_btn.clicked.connect(
            self.upload_folders
        )

    # ============================================
    # DEFAULT CENTERS
    # ============================================
    def load_default_centers(self):

        centers = [
            "Seethapathy",
            "CMC",
            "Rela",
        ]

        self.ui.center_choose_btn.addItems(centers)

    # ============================================
    # ADD NEW CENTER
    # ============================================
    def add_new_center(self):

        center_name, ok = QInputDialog.getText(
            self.ui.centralwidget,
            "Add Center",
            "Enter center name:",
        )

        if ok and center_name.strip():

            self.ui.center_choose_btn.addItem(
                center_name.strip()
            )

            self.ui.center_choose_btn.setCurrentText(center_name)

    # =================================================
    # MULTI FOLDER SELECTION
    # =================================================
    def select_folders(self):

        # ---------------------------------------------
        # START DIRECTORY
        # ---------------------------------------------
        start_path = "/"

        # ---------------------------------------------
        # CREATE DIALOG
        # ---------------------------------------------
        dialog = QFileDialog(
            self.ui.centralwidget,
            "Select Patient Folders",
            start_path,
        )

        # ---------------------------------------------
        # DIRECTORY MODE
        # ---------------------------------------------
        dialog.setFileMode(
            QFileDialog.Directory
        )

        # ---------------------------------------------
        # IMPORTANT
        # Native dialogs don't support proper
        # multi-folder selection
        # ---------------------------------------------
        dialog.setOption(
            QFileDialog.DontUseNativeDialog,
            True,
        )

        # ---------------------------------------------
        # ENABLE MULTI-SELECTION
        # ---------------------------------------------
        list_view = dialog.findChild(QListView)

        if list_view:

            list_view.setSelectionMode(
                QAbstractItemView.ExtendedSelection
            )

        tree_view = dialog.findChild(QTreeView)

        if tree_view:

            tree_view.setSelectionMode(
                QAbstractItemView.ExtendedSelection
            )

        # ---------------------------------------------
        # OPEN DIALOG
        # ---------------------------------------------
        if dialog.exec():

            folders = dialog.selectedFiles()

            for folder in folders:

                if folder not in self.selected_folders:

                    self.selected_folders.append(
                        folder
                    )

                    self.add_patient_card(folder)

                    print(
                        f"Selected Folder: {folder}"
                    )

    # =================================================
    # CREATE PATIENT CARD
    # =================================================
    def add_patient_card(self, folder_path):

        folder_path = Path(folder_path)

        patient_id = folder_path.name

        # ---------------------------------------------
        # COUNT FILES
        # ---------------------------------------------
        file_count = len(
            [
                f
                for f in folder_path.rglob("*")
                if f.is_file()
            ]
        )

        # ---------------------------------------------
        # CARD FRAME
        # ---------------------------------------------
        card = QFrame()

        card.setFixedSize(180, 120)

        card.setStyleSheet(
            """
            QFrame {
                background-color: #2b2b2b;
                border-radius: 12px;
                border: 1px solid #444444;
            }
            """
        )

        # ---------------------------------------------
        # CARD LAYOUT
        # ---------------------------------------------
        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setSpacing(15)

        # ---------------------------------------------
        # PATIENT ID LABEL
        # ---------------------------------------------
        lbl_patient = QLabel(patient_id)

        lbl_patient.setAlignment(
            Qt.AlignCenter
        )

        lbl_patient.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: white;
            """
        )

        # ---------------------------------------------
        # FILE COUNT LABEL
        # ---------------------------------------------
        lbl_count = QLabel(
            f"{file_count} files"
        )

        lbl_count.setAlignment(
            Qt.AlignCenter
        )

        lbl_count.setStyleSheet(
            """
            font-size: 14px;
            color: #bbbbbb;
            """
        )

        # ---------------------------------------------
        # ADD LABELS TO CARD
        # ---------------------------------------------
        layout.addWidget(lbl_patient)

        layout.addWidget(lbl_count)

        # ---------------------------------------------
        # ADD CARD TO HORIZONTAL LAYOUT
        # ---------------------------------------------
        self.ui.layout_patients.addWidget(
            card
        )

    # =================================================
    # UPLOAD / COPY FOLDERS
    # =================================================
    def upload_folders(self):

        if not self.selected_folders:

            QMessageBox.warning(
                self.ui.centralwidget,
                "No Folders",
                "Please select folders first.",
            )

            return

        center = (
            self.ui.center_choose_btn.currentText()
        )

        date = (
            self.ui.date_choose_btn
            .date()
            .toString("yyyy-MM-dd")
        )

        # ---------------------------------------------
        # OUTPUT DIRECTORY
        # ---------------------------------------------
        output_dir = (
            Config.ROOT_OUTPUT_DIR
            / center
            / date
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ---------------------------------------------
        # COPY EACH FOLDER
        # ---------------------------------------------
        for folder in self.selected_folders:

            src_path = Path(folder)

            dst_path = (
                output_dir / src_path.name
            )

            # Remove old folder
            if dst_path.exists():

                shutil.rmtree(dst_path)

            # Copy folder
            shutil.copytree(
                src_path,
                dst_path,
            )

            print(
                f"\nCopied:"
                f"\n{src_path}"
                f"\n->"
                f"\n{dst_path}\n"
            )

        # ---------------------------------------------
        # SUCCESS MESSAGE
        # ---------------------------------------------
        QMessageBox.information(
            self.ui.centralwidget,
            "Success",
            "Folders uploaded successfully.",
        )

        # ---------------------------------------------
        # CLEAR INTERNAL LIST
        # ---------------------------------------------
        self.selected_folders.clear()

        # ---------------------------------------------
        # CLEAR UI CARDS
        # ---------------------------------------------
        while self.ui.layout_patients.count():

            item = (
                self.ui.layout_patients.takeAt(0)
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()