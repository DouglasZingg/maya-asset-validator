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

        self.last_results = []
        self.filtered_results = []

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

    def export_report(self):
        from core.reporting import build_report, export_report_json, export_report_txt
    
        if not getattr(self, "last_results", None):
            QtWidgets.QMessageBox.information(
                self,
                "No Results",
                "Nothing to export yet. Run Validate Scene first."
            )
            return
    
        report = build_report(self.last_results)
    
        # Choose path + format
        default_name = f"{report['meta']['scene_name']}_validation_report.json"
    
        filepath, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Validation Report",
            default_name,
            "JSON Report (*.json);;Text Report (*.txt)"
        )
    
        if not filepath:
            self.status_label.setText("Export cancelled")
            return
    
        try:
            if filepath.lower().endswith(".txt") or "Text Report" in selected_filter:
                # ensure extension
                if not filepath.lower().endswith(".txt"):
                    filepath += ".txt"
                export_report_txt(filepath, report)
            else:
                if not filepath.lower().endswith(".json"):
                    filepath += ".json"
                export_report_json(filepath, report)
    
            self.status_label.setText(f"Report saved: {filepath}")
            self.add_result("INFO", f"Report exported to: {filepath}")
    
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not export report:\n{e}"
            )
            self.status_label.setText("Export failed")
    
    def apply_filters(self):
        # Filter settings
        severity = self.severity_filter.currentText()
        query = self.search_box.text().strip().lower()
    
        # Compute summary
        counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
        for r in self.last_results:
            lvl = r.get("level", "INFO")
            if lvl in counts:
                counts[lvl] += 1
    
        total = len(self.last_results)
        self.summary_label.setText(
            f"ERROR: {counts['ERROR']} | WARNING: {counts['WARNING']} | INFO: {counts['INFO']} | Total: {total}"
        )
    
        # Apply filters
        filtered = []
        for r in self.last_results:
            lvl = r.get("level", "INFO")
            node = (r.get("node") or "")
            msg = (r.get("message") or "")
    
            if severity != "All" and lvl != severity:
                continue
    
            if query:
                hay = f"{lvl} {node} {msg}".lower()
                if query not in hay:
                    continue
    
            filtered.append(r)
    
        self.filtered_results = filtered
    
        # Rebuild UI list
        self.results_list.clear()
        if not filtered:
            self.add_result("INFO", "No results match current filters")
            return
    
        for r in filtered:
            display = f"{r.get('node','')} — {r.get('message','')}"
            item = QtWidgets.QListWidgetItem(f"[{r.get('level','INFO')}] {display}")
            # Store the node on the item for double-click selection
            item.setData(QtCore.Qt.UserRole, r.get("node", ""))
    
            # Color
            lvl = r.get("level", "INFO")
            if lvl == "ERROR":
                item.setForeground(QtGui.QColor("red"))
            elif lvl == "WARNING":
                item.setForeground(QtGui.QColor("orange"))
            else:
                item.setForeground(QtGui.QColor("white"))
    
            self.results_list.addItem(item)

    def on_result_double_clicked(self, item):
        import maya.cmds as cmds
    
        node = item.data(QtCore.Qt.UserRole)
        if not node:
            return
    
        if cmds.objExists(node):
            cmds.select(node, r=True)
            self.status_label.setText(f"Selected: {node}")
        else:
            self.status_label.setText("Object no longer exists in scene")

    def clear_results(self):
        self.results_list.clear()
        self.last_results = []
        self.filtered_results = []
        if hasattr(self, "summary_label"):
            self.summary_label.setText("ERROR: 0 | WARNING: 0 | INFO: 0 | Total: 0")
        self.status_label.setText("Results cleared")


    # ---------------------------
    # UI Construction
    # ---------------------------
    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QLabel("Asset Validation Tool")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header)

        # --- Filters Row ---
        filter_layout = QtWidgets.QHBoxLayout()

        self.severity_filter = QtWidgets.QComboBox()
        self.severity_filter.addItems(["All", "ERROR", "WARNING", "INFO"])

        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Search results... (node, message)")

        filter_layout.addWidget(QtWidgets.QLabel("Filter:"))
        filter_layout.addWidget(self.severity_filter)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(self.search_box)

        main_layout.addLayout(filter_layout)

        # --- Summary ---
        self.summary_label = QtWidgets.QLabel("ERROR: 0 | WARNING: 0 | INFO: 0 | Total: 0")
        self.summary_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.summary_label)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.validate_btn = QtWidgets.QPushButton("Validate Scene")
        self.clear_btn = QtWidgets.QPushButton("Clear Results")
        self.autofix_btn = QtWidgets.QPushButton("Auto Fix")
        self.export_btn = QtWidgets.QPushButton("Export Report")

        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.autofix_btn)
        button_layout.addWidget(self.export_btn)
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
        self.export_btn.clicked.connect(self.export_report)
        self.severity_filter.currentIndexChanged.connect(self.apply_filters)
        self.search_box.textChanged.connect(self.apply_filters)
        self.results_list.itemDoubleClicked.connect(self.on_result_double_clicked)


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
        
        self.last_results = results
    
        self.last_results = results
        self.apply_filters()
    
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
