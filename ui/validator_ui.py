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
        
    def run_auto_fix(self):
        from core.auto_fix import run_auto_fix
    
        # Confirmation dialog
        msg = (
            "Auto Fix will attempt to:\n"
            "• Freeze transforms (mesh objects)\n"
            "• Center pivots (mesh objects)\n"
            "• Delete unused nodes\n\n"
            "This is undoable with a single Ctrl+Z.\n\n"
            "Continue?"
        )
    
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Auto Fix",
            msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
    
        if reply != QtWidgets.QMessageBox.Yes:
            self.status_label.setText("Auto Fix cancelled")
            return
    
        self.status_label.setText("Running Auto Fix...")
        actions = run_auto_fix()
    
        # Show what happened
        for a in actions:
            msg = f"{a['node']} — {a['message']}"
            self.add_result(a["level"], msg)
    
        self.status_label.setText("Auto Fix complete")


    # ---------------------------
    # UI Construction
    # ---------------------------
    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QLabel("Asset Validation Tool")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.validate_btn = QtWidgets.QPushButton("Validate Scene")
        self.clear_btn = QtWidgets.QPushButton("Clear Results")
        self.autofix_btn = QtWidgets.QPushButton("Auto Fix")

        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.autofix_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Results list
        self.results_list = QtWidgets.QListWidget()
        self.results_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        main_layout.addWidget(self.results_list)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.status_label)

    # ---------------------------
    # Signal Connections
    # ---------------------------
    def connect_signals(self):
        self.validate_btn.clicked.connect(self.run_validation)
        self.autofix_btn.clicked.connect(self.run_auto_fix)
        self.clear_btn.clicked.connect(self.clear_results)

    # ---------------------------
    # Validation Logic
    # ---------------------------
    def run_validation(self):
        from core.naming_checks import run_naming_checks
        from core.transform_checks import run_transform_checks
        from core.geometry_checks import run_geometry_checks
        from core.texture_checks import run_texture_checks
    
        self.results_list.clear()
        self.status_label.setText("Running validation...")
    
        results = []
        results.extend(run_naming_checks())
        results.extend(run_transform_checks())
        results.extend(run_geometry_checks())
        results.extend(run_texture_checks())
    
        if not results:
            self.add_result("INFO", "Scene passed validation")
        else:
            for result in results:
                msg = f"{result['node']} — {result['message']}"
                self.add_result(result["level"], msg)
    
        self.status_label.setText("Validation complete")


    def clear_results(self):
        self.results_list.clear()
        self.status_label.setText("Results cleared")

    def add_result(self, level, message):
        item = QtWidgets.QListWidgetItem(f"[{level}] {message}")

        # Color coding
        if level == "ERROR":
            item.setForeground(QtGui.QColor("red"))
        elif level == "WARNING":
            item.setForeground(QtGui.QColor("orange"))
        else:
            item.setForeground(QtGui.QColor("white"))

        self.results_list.addItem(item)


# ---------------------------
# Window Launcher
# ---------------------------
def show():
    global asset_validator_window
    try:
        asset_validator_window.close()
        asset_validator_window.deleteLater()
    except Exception:
        pass

    asset_validator_window = AssetValidatorUI()
    asset_validator_window.show()
