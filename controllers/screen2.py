import shutil
from pathlib import Path

from PySide6.QtCore import QObject, QDate, Qt
from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
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

        # =====================================
        # VALIDATE STRUCTURE
        # =====================================

        visit_dirs = [
            d
            for d in folder_path.iterdir()
            if d.is_dir()
        ]

        num_visits = len(visit_dirs)

        structure_ok = True
        reason = ""

        # Rule 1: 1-5 visits
        if num_visits < 1 or num_visits > 5:

            structure_ok = False
            reason = f"{num_visits} visits"

        # Rule 2: Every visit contains DICOMs
        if structure_ok:

            for visit in visit_dirs:

                dicom_count = len(
                    list(visit.glob("*.dcm"))
                )

                if dicom_count == 0:

                    structure_ok = False
                    reason = f"No DICOMs in {visit.name}"
                    break

        # Rule 3: No DICOMs in root
        if structure_ok:

            root_dicoms = len(
                list(folder_path.glob("*.dcm"))
            )

            if root_dicoms > 0:

                structure_ok = False
                reason = "DICOMs in root folder"

        # =====================================
        # FILE COUNT
        # =====================================

        file_count = len(
            [
                f
                for f in folder_path.rglob("*")
                if f.is_file()
            ]
        )

        # =====================================
        # CARD COLORS
        # =====================================

        if structure_ok:
            status_text = "Valid"
        else:
            status_text = "Invalid"

        # =====================================
        # CARD
        # =====================================

        card = QFrame()

        card.folder_path = str(folder_path)

        card.setFixedSize(220, 160)

        card.setToolTip(reason)

        card.setStyleSheet(
            """
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            """
        )

        layout = QVBoxLayout(card)

        # =====================================
        # TOP BAR
        # =====================================

        top_bar = QHBoxLayout()

        top_bar.addStretch()

        btn_remove = QPushButton("✕")

        btn_remove.setFixedSize(20, 20)

        btn_remove.clicked.connect(
            lambda checked=False,
            c=card,
            p=str(folder_path):
            self.remove_patient_card(c, p)
        )

        top_bar.addWidget(btn_remove)

        layout.addLayout(top_bar)

        # =====================================
        # LABELS
        # =====================================

        lbl_patient = QLabel(patient_id)

        lbl_patient.setAlignment(Qt.AlignCenter)

        lbl_patient.setStyleSheet(
            """
            font-size:16px;
            font-weight:bold;
            """
        )

        lbl_files = QLabel(
            f"Files : {file_count}"
        )

        lbl_files.setAlignment(Qt.AlignCenter)

        visit_info = []

        for idx, visit in enumerate(visit_dirs, start=1):

            file_count_visit = len(
                [
                    f
                    for f in visit.rglob("*")
                    if f.is_file()
                ]
            )

            visit_info.append(
                f"V{idx}: {file_count_visit}"
            )
            
        lbl_visits = QLabel(
            f"Visits : {num_visits}"
        )

        lbl_visits.setAlignment(Qt.AlignCenter)

        lbl_visit_details = QLabel(
            "\n".join(visit_info)
        )

        lbl_visit_details.setAlignment(
            Qt.AlignCenter
        )

        lbl_visit_details.setWordWrap(True)

        lbl_status = QLabel(
            f"Status : {status_text}"
        )

        lbl_status.setAlignment(Qt.AlignCenter)


        layout.addWidget(lbl_patient)
        layout.addWidget(lbl_files)
        layout.addWidget(lbl_visits)
        layout.addWidget(lbl_visit_details)
        layout.addWidget(lbl_status)

        self.ui.layout_patients.addWidget(card)

    def remove_patient_card(
        self,
        card,
        folder_path,
    ):

        if folder_path in self.selected_folders:

            self.selected_folders.remove(
                folder_path
            )

        self.ui.layout_patients.removeWidget(
            card
        )

        card.deleteLater()

        print(
            f"Removed: {folder_path}"
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