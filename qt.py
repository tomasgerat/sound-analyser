import sys

if 'PyQt5' in sys.modules:
    # PyQt5
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, QSettings
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressDialog, QMessageBox, QLayout, QVBoxLayout, QCheckBox

else:
    # PySide2
    from PySide2 import QtGui, QtWidgets, QtCore
    from PySide2.QtCore import Signal, Slot, QSettings
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QApplication, QMainWindow, QProgressDialog, QMessageBox, QLayout, QVBoxLayout, QCheckBox
