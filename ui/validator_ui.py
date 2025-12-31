# Qt compatibility across Maya versions
try:
    # Maya 2025+ (Qt6)
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    try:
        # Maya 2020–2024 (Qt5)
        from PySide2 import QtWidgets, QtCore, QtGui
        from shiboken2 import wrapInstance
    except ImportError:
        # Maya 2017–2019 (Qt4)
        from PySide import QtGui, QtCore
        from shiboken import wrapInstance
        QtWidgets = QtGui

import maya.OpenMayaUI as omui

def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class AssetValidatorUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle("Maya Asset Validator")
        self.setMinimumSize(500, 400)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.build_ui()
        self.connect_signals()
        
    def clear_results(self):
        self.results_list.clear()
        self.status_label.setText("Results cleared")
        
    def add_result(self, level, message):
        item = QtWidgets.QListWidgetItem(f"[{level}] {message}")

        if level == "ERROR":
            item.setForeground(QtGui.QColor("red"))
        elif level == "WARNING":
            item.setForeground(QtGui.QColor("orange"))
        else:
            item.setForeground(QtGui.QColor("white"))

        self.results_list.addItem(item)

    # ---------------------------
    # UI Construction
    # ---------------------------
    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # --- Header ---
        header = QtWidgets.QLabel("Asset Validation Tool")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header)

        # --- Buttons ---
        button_layout = QtWidgets.QHBoxLayout()

        self.validate_btn = QtWidgets.QPushButton("Validate Scene")
        self.clear_btn = QtWidgets.QPushButton("Clear Results")

        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # --- Results List ---
        self.results_list = QtWidgets.QListWidget()
        self.results_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        main_layout.addWidget(self.results_list)

        # --- Status Bar ---
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.status_label)

    # ---------------------------
    # Signal Connections
    # ---------------------------
    def connect_signals(self):
        self.validate_btn.clicked.connect(self.run_validation)
        self.clear_btn.clicked.connect(self.clear_results)

    # ---------------------------
    # Validation Logic
    # ---------------------------
    def run_validation(self):
        from core.naming_checks import run_naming_checks

        self.results_list.clear()
        self.status_label.setText("Running validation...")

        results = run_naming_checks()

        if not results:
            self.add_result("INFO", "Scene passed naming validation")
        else:
            for result in results:
                msg = f"{result['node']} — {result['message']}"
                self.add_result(result["level"], msg)

        self.status_label.setText("Validation complete")

# ---------------------------
# Window Launcher
# ---------------------------
def show():
    global asset_validator_window
    try:
        asset_validator_window.close()
        asset_validator_window.deleteLater()
    except:
        pass

    asset_validator_window = AssetValidatorUI()
    asset_validator_window.show()
