from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui

def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle("PySide6 Test - Maya 2026")
        self.setMinimumWidth(300)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("PySide6 is working in Maya 2026"))

def show_window():
    global window
    try:
        window.close()
        window.deleteLater()
    except:
        pass

    window = TestWindow()
    window.show()

show_window()
