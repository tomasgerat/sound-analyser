# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import shutil
import sys
from os import listdir
from os.path import isfile, join
import pyaudio
import wave
import time
import math

from analyser import Analyser

from ui_mainWindow import Ui_MainWindow
from qt import *
from m_checkbox import M_CheckBox
from m_settings import M_Settings

MODEL_PATH = "./model/"
TMP_PATH = "./tmp/"
INPUT_FILE = "./sample/money.wav"
INPUT_FILES_DIR = "./sample/"
SETTINGS = "./Analyser.ini"
SETTINGS = "./Analyser.CFG"

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Sound Analyser GUI")
        self.setWindowIcon(QIcon('icon.png'))
        self.pLoadBtn.clicked.connect(self.on_load_records)
        self.pAnalyseBtn.clicked.connect(self.on_analyse)
        self.pPlayBtnDetected.clicked.connect(self.on_play_records_detected)
        self.pStopBtnDetected.clicked.connect(self.on_stop_playing_records_detected)
        self.pPlayBtnNotDetected.clicked.connect(self.on_play_records_not_detected)
        self.pStopBtnNotDetected.clicked.connect(self.on_stop_playing_records_not_detected)
        self.pSelectModelBtn.clicked.connect(self.on_select_model)
        self.pInitAnalyserBtn.clicked.connect(self.on_init_analyser)
        self.pSplitPerSeconds.valueChanged.connect(self.on_split_per_second_changed)
        self.pOverlap.valueChanged.connect(self.on_overlap_changed)
        self.pFindClass.textEdited.connect(self.on_find_classes)
        self.pChckBoxOnlyAccepted.stateChanged.connect(self.on_find_classes)
        self.pAnalyseBtn.setDisabled(True)
        self.stopPlay = False
        self.analyser = None
        self.waitDialog = None
        self.detected = None
        self.notDetected = None
        self.on_load_records()
        self.on_init_analyser()
        self.show()

    @Slot()
    def on_init_analyser(self):
        print("[INIT ANALYSER]")
        self.show_wait_dialog("Initialising analyser...")
        self.analyser = Analyser(self.pModelPath.text(), TMP_PATH, int(self.pSplitPerSeconds.text()), int(self.pOverlap.text()))
        if self.analyser.is_ready() is True:
            self.pAnalyseBtn.setDisabled(False)
            self.load_classes(self.analyser.class_names)
        else:
            self.pAnalyseBtn.setDisabled(True)
            self.analyser = None
        self.remove_wait_dialog()
    @Slot()
    def on_select_model(self):
        open_dir = QFileDialog().getExistingDirectory(self, caption='Select model directory', directory="./",
                                                      options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        print("Selected directory: ", open_dir)
        self.pModelPath.setText(open_dir)

    @Slot()
    def on_load_records(self):
        print("[LOAD RECORDS]")
        self.pRecordsList.clear()
        files = [INPUT_FILES_DIR + f for f in listdir(INPUT_FILES_DIR) if isfile(join(INPUT_FILES_DIR, f))]
        files.sort()
        for i, input_f in enumerate(files):
            print(str(i) + " ", input_f)
            self.pRecordsList.addItem(input_f)
            if i == 0:
                self.pRecordsList.setCurrentRow(0)
    @Slot()
    def on_analyse(self):
        print("[ANALYSE]")
        self.pAnalyseBtn.setDisabled(True)
        for item in self.pRecordsList.selectedItems():
            path = item.text()
            self.show_wait_dialog("Analysing " + path)
            self.clear_tmp()
            start = time.time()
            print("Working on", path, "...")
            #list of tupples [(filename, class, start second in original)]
            self.detected, self.notDetected =  self.analyser.test_file(path)
            if len(self.detected) > 0:
                print("Record: ", path, "contains voice!")
            else:
                print("Record: ", path, " NOT contains voice!")
            self.pDetectedRecordsList.clear()
            self.pNotDetectedRecordsList.clear()
            for (filename, c, second) in self.detected:
                self.pDetectedRecordsList.addItem(filename+"* "+c+"* original start sec: " + str(second))
            for (filename, c, second) in self.notDetected:
                self.pNotDetectedRecordsList.addItem(filename+"* "+c+"* original start sec: " + str(second))
            end = time.time()
            elapsedTime = "Elapsed time: " + str(math.ceil(end - start)) + " sec"
            self.pStatusLabel.setText(elapsedTime)
            print(elapsedTime)
            self.remove_wait_dialog()
        self.pAnalyseBtn.setDisabled(False)

    @Slot()
    def on_play_records_detected(self):
        print("[PLAY]")
        self.pPlayBtnDetected.setDisabled(True)
        self.pPlayBtnNotDetected.setDisabled(True)
        self.pAnalyseBtn.setDisabled(True)
        for item in self.pDetectedRecordsList.selectedItems():
            txt = str(item.text())
            self.play_record(txt[0:txt.index("*")])
        self.pPlayBtnDetected.setDisabled(False)
        self.pPlayBtnNotDetected.setDisabled(False)
        self.pAnalyseBtn.setDisabled(False)

    @Slot()
    def on_play_records_not_detected(self):
        print("[PLAY]")
        self.pPlayBtnDetected.setDisabled(True)
        self.pPlayBtnNotDetected.setDisabled(True)
        self.pAnalyseBtn.setDisabled(True)
        for item in self.pNotDetectedRecordsList.selectedItems():
            txt = str(item.text())
            self.play_record(txt[0:txt.index("*")])
        self.pPlayBtnDetected.setDisabled(False)
        self.pPlayBtnNotDetected.setDisabled(False)
        self.pAnalyseBtn.setDisabled(False)

    def play_record(self, path):
        print("Playing", path)
        chunk = 1024
        #open a wav format music
        f = wave.open(path,"rb")
        p = pyaudio.PyAudio()
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()), channels = f.getnchannels(),
                        rate = f.getframerate(), output = True)
        self.stopPlay = False
        data = f.readframes(chunk)
        while data:
            stream.write(data)
            QApplication.processEvents();
            if self.stopPlay is True:
                break
            data = f.readframes(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()


    @Slot()
    def on_stop_playing_records_detected(self):
        self.stopPlay = True

    @Slot()
    def on_stop_playing_records_not_detected(self):
        self.stopPlay = True

    @Slot()
    def on_find_classes(self):
        layout = self.pClasses.layout()
        for i in range(0, layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                if self.pFindClass.text().lower() in widget.text().lower():
                    if self.pChckBoxOnlyAccepted.isChecked():
                        if widget.isChecked():
                            widget.show()
                        else:
                            widget.hide()
                    else:
                        widget.show()
                else:
                    widget.hide()

    def show_wait_dialog(self, text):
        if self.waitDialog is not None:
            self.waitDialog.close()
        self.waitDialog = QMessageBox(self)
        self.waitDialog.setWindowTitle("Please wait...")
        self.waitDialog.setText(text)
        self.waitDialog.setModal(QtCore.Qt.WindowModal)
        self.waitDialog.show()
        self.waitDialog.setStandardButtons(QMessageBox.NoButton)
        self.update()
        QApplication.processEvents()

    def remove_wait_dialog(self):
        if self.waitDialog is not None:
            self.waitDialog.close()
        self.waitDialog = None
        self.update()
        QApplication.processEvents()

    def clear_tmp(self):
        if os.path.exists(TMP_PATH):
            shutil.rmtree(TMP_PATH)
        Path(TMP_PATH).mkdir(parents=True, exist_ok=True)
        return

    @Slot(int)
    def on_split_per_second_changed(self, val):
        if int(self.pOverlap.text()) >= val:
            self.pOverlap.setValue(val-1)

    @Slot(int)
    def on_overlap_changed(self, val):
        if int(self.pSplitPerSeconds.text()) <= val:
            self.pSplitPerSeconds.setValue(val+1)

    def load_classes(self, classes):
        print("[Load classes]")
        setting = M_Settings(SETTINGS)
        accepted_classes = setting.get_accepted_classes()
        if self.analyser is not None:
            self.analyser.set_accepted_classes(accepted_classes)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        for i,c in enumerate(classes):
            print("Add class:", c)
            checkbox = M_CheckBox(i, self.pClasses)
            checkbox.setText(c)
            if c in  accepted_classes:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_class_checked)
            layout.addWidget(checkbox)
        layout.addStretch(1)
        self.pClasses.setLayout(layout)
        self.update()
        QApplication.processEvents()

    @Slot()
    def on_class_checked(self):
        layout = self.pClasses.layout()
        accepted_classes = []
        for i in range(0, layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                if widget.isChecked():
                    accepted_classes.append(widget.text())
        settings = M_Settings(SETTINGS)
        settings.set_accepted_classes(accepted_classes)
        if self.analyser is not None:
            self.analyser.set_accepted_classes(accepted_classes)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    ret = app.exec_()
    sys.exit( ret )
