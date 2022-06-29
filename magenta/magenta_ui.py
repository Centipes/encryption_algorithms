
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,QHBoxLayout, QVBoxLayout,
                             QComboBox, QLineEdit, QSpacerItem, QSizePolicy, QRadioButton, QButtonGroup, QProgressBar, QFileDialog)
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt

import sys, os
import random

import magenta as m
import file_system as fs
import stylesheet as s

ICON_KEY = "../icons/key.png"
ICON_SHOW_KEY = "../icons/show_key_light.png"
ICON_HIDE_KEY = "../icons/hide_key_light.png"
ICON_SHOW_FILE = "../icons/show_key_dark.png"
ICON_GEN_KEY = "../icons/box.png"
ICON_COPY_KEY = "../icons/copy.png"
ICON_SAVE_KEY = "../icons/save.png"

class MainWindow(QWidget):
    sgnStop = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magenta cipher")
        self.setGeometry(100, 100, 1300, 500)
        self.file_system = fs.FileSystemTree()
        self.file_system.setStyleSheet(s.tree_style)
        self.setObjectName("main")
        self.UiComponents()
        self.show()

    def resizeEvent(self, event):
        if(self.cipher_widget.width()>1000):
            width = self.cipher_widget.width()
            self.chars = self.filename.width()*12//120
        else:
            width = 1000
            self.chars = 12
        self.key_widget.setGeometry(43, 80, width-160, 50)
        self.file_info.setGeometry(110, 200, width-222, 140)
        self.stop_button.setGeometry(width-324, 301, 200, 16)
        self.progress_label.setGeometry(282, 320, width-880, 30)
        self.filename.setText(self.short_filename(self.file_system.filename, self.chars))

        QWidget.resizeEvent(self, event)

    def closeEvent(self, event):
        self.stop_thread()
        event.accept()

    def UiKey(self):

        self.key_widget = QWidget(self.cipher_widget)
        key_label = QLabel("key")
        key_label.setFixedSize(30,20)

        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.Password)
        self.key_edit.setMaximumHeight(18)
        font = QFont("Monospace", 9)
        font.setStyleHint(QFont.Monospace)
        self.key_edit.setFont(font)

        self.show_key_button = QPushButton()
        self.show_key_button.setIcon(QIcon(QPixmap(ICON_SHOW_KEY)))
        self.show_key_button.setToolTip("show key")
        self.show_key_button.clicked.connect(self.show_key)
        self.show_key_button.setObjectName("action_key_button")

        key_from_file_button = QPushButton()
        key_from_file_button.setIcon(QIcon(QPixmap(ICON_KEY)))
        key_from_file_button.setToolTip("key from file")
        key_from_file_button.clicked.connect(self.read_key)
        key_from_file_button.setObjectName("action_key_button")

        key_generation_button = QPushButton()
        key_generation_button.setIcon(QIcon(QPixmap(ICON_GEN_KEY)))
        key_generation_button.setToolTip("generate a key")
        key_generation_button.clicked.connect(self.generate_key)
        key_generation_button.setObjectName("action_key_button")

        copy_key_button = QPushButton()
        copy_key_button.setIcon(QIcon(QPixmap(ICON_COPY_KEY)))
        copy_key_button.setToolTip("copy key to clipboard")
        copy_key_button.clicked.connect(self.copy_key)
        copy_key_button.setObjectName("action_key_button")

        save_key_to_file_button = QPushButton()
        save_key_to_file_button.setIcon(QIcon(QPixmap(ICON_SAVE_KEY)))
        save_key_to_file_button.setToolTip("save key to file")
        save_key_to_file_button.clicked.connect(self.save_key)
        save_key_to_file_button.setObjectName("action_key_button")

        verticalSpacer = QSpacerItem(10, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        key_layout = QHBoxLayout(self.key_widget)
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_edit)
        key_layout.addWidget(self.show_key_button)
        key_layout.addWidget(key_from_file_button)
        key_layout.addWidget(key_generation_button)
        key_layout.addItem(verticalSpacer)
        key_layout.addWidget(copy_key_button)
        key_layout.addWidget(save_key_to_file_button)
        key_layout.setSpacing(3)

        key_sizes_widget = QWidget(self.cipher_widget)
        key_sizes_widget.setGeometry(50, 120, 300, 50)

        self.bits = 128
        self.radio_button_128 = QRadioButton('128 bits')
        self.radio_button_128.setChecked(True)
        self.radio_button_192 = QRadioButton('192 bits')
        self.radio_button_256 = QRadioButton('256 bits')

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.radio_button_128, 128)
        self.button_group.addButton(self.radio_button_192, 192)
        self.button_group.addButton(self.radio_button_256, 256)

        key_sizes_layout = QHBoxLayout(key_sizes_widget)
        key_sizes_layout.addWidget(self.radio_button_128)
        key_sizes_layout.addWidget(self.radio_button_192)
        key_sizes_layout.addWidget(self.radio_button_256)

        self.button_group.buttonClicked.connect(self.change_bits)

    def UiFileInfo(self):
        plaintext_label = QLabel("plaintext", self.cipher_widget)
        plaintext_label.setGeometry(53, 245, 100, 50)

        self.file_info = QWidget(self.cipher_widget)

        name_label = QLabel("Filename")
        type_label = QLabel("Type")
        size_label = QLabel("Size")
        date_label = QLabel("Date")
        space_label = QSpacerItem(249, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        form_hlayout = QHBoxLayout()
        form_hlayout.addWidget(name_label)
        form_hlayout.addWidget(type_label)
        form_hlayout.addWidget(size_label)
        form_hlayout.addWidget(date_label)
        form_hlayout.addItem(space_label)
        form_hlayout.setSpacing(1)

        self.filename = QLabel()
        self.filetype = QLabel()
        self.filesize = QLabel()
        self.filedate = QLabel()
        file_labels = (self.filename, self.filetype, self.filesize, self.filedate)

        show_file_button = QPushButton(self)
        show_file_button.setFixedSize(38, 38)
        show_file_button.setIcon(QIcon(QPixmap(ICON_SHOW_FILE)))
        show_file_button.setObjectName("show_button")
        show_file_button.clicked.connect(lambda: self.show_file (self.file_system.filepath))

        self.file_layout = QHBoxLayout()
        self.file_layout.addWidget(self.filename)
        self.file_layout.addWidget(self.filetype)
        self.file_layout.addWidget(self.filesize)
        self.file_layout.addWidget(self.filedate)
        self.file_layout.addWidget(show_file_button)
        self.file_layout.setSpacing(1)

        for i in range(4):
            form_hlayout.itemAt(i).setAlignment(QtCore.Qt.AlignCenter)
            file_labels[i].setAlignment(QtCore.Qt.AlignCenter)
            file_labels[i].setObjectName("fileinfo_label")

        self.form_vlayout = QVBoxLayout(self.file_info)
        self.form_vlayout.addLayout(form_hlayout)
        self.form_vlayout.addLayout(self.file_layout)
        self.form_vlayout.setSpacing(1)

    def UiProgress(self):

        self.bar = QProgressBar()
        self.bar.setValue(0)
        self.bar.setAlignment(Qt.AlignCenter)

        self.size_label = QLabel("0B")
        self.size_label.setFixedSize(100, 39)
        self.size_label.setAlignment(QtCore.Qt.AlignCenter)

        self.progress_label = QLabel(self.cipher_widget)
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)

        self.time_label = QLabel()
        self.time_label.setFixedSize(80, 28)
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)

        self.exec_file = QLabel()
        self.exec_file.setFixedSize(124, 28)
        self.exec_file.setAlignment(QtCore.Qt.AlignCenter)

        self.bar_layout = QHBoxLayout()
        self.bar_layout.addWidget(self.bar)
        self.bar_layout.addWidget(self.size_label)
        self.bar_layout.addWidget(self.time_label)
        self.bar_layout.addWidget(self.exec_file)
        self.bar_layout.setSpacing(1)
        self.form_vlayout.addLayout(self.bar_layout)


    def UiControl(self):
        self.enc_button = QPushButton("encrypt", self.cipher_widget)
        self.enc_button.setObjectName("enc_button")
        self.enc_button.clicked.connect(lambda: self.start_thread("enc"))
        self.enc_button.setFixedSize(100,30)

        self.dec_button = QPushButton("decrypt", self.cipher_widget)
        self.dec_button.setObjectName("dec_button")
        self.dec_button.clicked.connect(lambda: self.start_thread("dec"))
        self.dec_button.setFixedSize(100,30)

        self.stop_button = QPushButton("stop", self.cipher_widget)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.stop_process)
        self.stop_button.hide()

        verticalSpacer = QSpacerItem(10, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.file_layout.addItem(verticalSpacer)
        self.file_layout.addWidget(self.enc_button)
        self.file_layout.addWidget(self.dec_button)


    def UiComponents(self):

        self.communicate = self.file_system.file_is_changed.connect(self.update_fileinfo)
        self.cipher_widget = QWidget()
        self.cipher_widget.setGeometry(0,0,1000, 500)
        self.cipher_widget.setObjectName("cipher")

        cipher_label = QLabel("MAGENTA",self.cipher_widget)
        cipher_label.setGeometry(10, 0, 400, 50)
        cipher_label.setFont(QFont('Times', 30))
        self.cipher_mode_label = QLabel("cipher block mode", self.cipher_widget)
        self.cipher_mode_label.setGeometry(53, 175, 200, 30)

        mode_list = ["ECB", "CBC", "CFB", "OFB"]
        self.cipher_mode = QComboBox(self.cipher_widget)
        self.cipher_mode.setStyleSheet(s.combobox_style)
        self.cipher_mode.setGeometry(180, 175, 100, 30)
        self.cipher_mode.addItems(mode_list)
        # self.cipher_mode.addItem("ECB", lambda p: None)
        # self.cipher_mode.addItem("CBC", lambda p: m.CBC(p))
        # self.cipher_mode.addItem("CFB", lambda p: m.CFB(p))
        # self.cipher_mode.addItem("OFB", lambda p: m.OFB(p))
        # self.cipher_mode.addItem("CTR", lambda p: m.CTR(p))

        self.UiKey()
        self.UiFileInfo()
        self.UiProgress()
        self.UiControl()

        self.widget_layout = QHBoxLayout(self)
        self.widget_layout.addWidget(self.file_system, stretch=1)
        self.widget_layout.addWidget(self.cipher_widget, stretch=3)
        self.widget_layout.setSpacing(0)

        self.error_label = QLabel("Error:", self.cipher_widget)
        self.error_label.setGeometry(120, 400, 800, 30)
        self.error_label.hide()

    def short_filename(self, fname, cs):
        return (fname[:cs] + "..") if len(fname)> cs else fname

    def change_bits(self):
        self.bits = self.button_group.checkedId()

    def print_error(self, text, suffix):
        self.progress_label.setText(suffix + "ryption error")
        self.error_label.setText(text % suffix)
        self.error_label.show()

    def start_thread(self, suffix):
        if(hasattr(self, "enc_dec_thread") and self.enc_dec_thread.isRunning()):
            return
        self.counter = 0
        self.bar.setValue(0)
        self.time_label.setText("")
        self.exec_file.setText("")
        self.error_label.hide()
        self.progress_label.setText("preparing...")
        self.suffix = suffix

        if(self.file_system.filetype == ""):
            self.print_error("Error: specify the file to %srypt", suffix)
            return

        if(self.key_edit.text() == ""):
            self.print_error("Error: a key is required for %sryption", suffix)
            return

        # cb_mode = self.cipher_mode.currentData()(self.key_edit.text())
        cb_mode = self.cipher_mode.currentText()

        filename = os.path.splitext(os.path.basename(self.filepath))
        basename = filename[0]
        type = filename[1]
        basename = os.path.splitext(basename)[0] if (os.path.splitext(basename)[1] in (".dec",".enc")) else basename

        filepath_out = os.path.dirname(self.filepath) +'/' + basename + "." + suffix + type

        self.enc_dec_thread = m.CryptoThread(self.bits, self.key_edit.text(), suffix, self.filepath, filepath_out, cb_mode, self)
        self.sgnStop.connect(self.enc_dec_thread.stop)
        self.enc_dec_thread.update.connect(self.update_progress)

        self.enc_dec_thread.start()
        self.progress_label.setText(suffix+"rypting...")
        self.stop_button.show()

    def stop_thread(self):
        if(hasattr(self, "enc_dec_thread") and self.enc_dec_thread.isRunning()):
            self.sgnStop.emit()
            self.enc_dec_thread.wait()

    def stop_process(self):
        self.stop_thread()
        self.stop_button.hide()
        self.progress_label.setText(self.suffix + "ryption stopped")

    def show_file(self, name):
        os.startfile(name)

    def set_enabled(self, enc_bool, dec_bool):
        self.enc_button.setEnabled(enc_bool)
        self.dec_button.setEnabled(dec_bool)

    def update_fileinfo(self):
        fname = self.file_system.filename

        if(os.path.splitext(fname)[1]=='.enc'):
            self.set_enabled(False, True)
        elif(os.path.splitext(fname)[1]=='.dec'):
            self.set_enabled(True, False)
        else:
            self.set_enabled(True, True)

        self.filename.setText(self.short_filename(fname, self.chars))
        self.filepath = self.file_system.filepath
        self.filename.setToolTip(self.filepath)
        self.filetype.setText(self.file_system.filetype)
        self.filesize.setText(self.file_system.filesize)
        self.filedate.setText(self.file_system.filedate)

    def update_progress(self, val):
        self.bar.setValue(val[0])
        self.counter += val[1]
        self.size_label.setText(self.file_system.convert_bytes(self.counter))

        if(val[0]==100):
            self.add_form()
            self.stop_button.hide()
        elif(val[1]==0):
            self.print_error("Error: the wrong key or encryption type is selected. Unable to continue %srypting.", self.suffix)
            self.stop_button.hide()

    def add_form(self):
        self.progress_label.setText(self.suffix+"ryption is done")
        self.time_label.setText("time: %.2fs" % self.enc_dec_thread.time)

        exec_filename = self.enc_dec_thread.fname_to
        self.exec_file.setText(self.short_filename(os.path.basename(exec_filename), 16))
        self.exec_file.setToolTip(exec_filename)

    def generate_key(self):
        import secrets
        import string

        length = random.randint(8, 25)
        letters_and_digits = string.ascii_letters + string.digits
        crypt_rand_string = ''.join(secrets.choice(letters_and_digits) for i in range(length))
        self.key_edit.setText(crypt_rand_string)

    def show_key(self):
        icon, type = (ICON_HIDE_KEY, QLineEdit.Normal) if (self.key_edit.echoMode() == QLineEdit.Password) else (ICON_HIDE_KEY, QLineEdit.Password)
        self.show_key_button.setIcon(QIcon(QPixmap(icon)))
        self.key_edit.setEchoMode(type)

    def read_key(self):
        fileName = QFileDialog.getOpenFileName(self, "Read key", "*.txt")
        if fileName[0]:
            file_key = open(fileName[0], 'r')
            self.key_edit.setText(file_key.read())

    def copy_key(self):
        import subprocess
        cmd='echo|set /p=%s|clip' %self.key_edit.text()
        subprocess.check_call(cmd, shell=True)

    def save_key(self):
        filename = QFileDialog.getSaveFileName(self, "Save key", "*.txt")
        if filename[0]:
            file = open(filename[0], "w")
            file.write(self.key_edit.text())
            file.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(s.style)
    win = MainWindow()
    sys.exit(app.exec())
