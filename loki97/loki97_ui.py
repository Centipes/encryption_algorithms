import sys, os
from PyQt5.QtWidgets import (QWidget, QComboBox, QApplication, QLineEdit, QMainWindow,
                             QHBoxLayout, QProgressBar, QVBoxLayout, QFileDialog, QPushButton, QLabel)
from PyQt5.QtGui import QIcon, QPixmap
import loki97 as lk


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(350, 100, 500, 0)
        self.setWindowTitle("Loki97")
        self.initUI()

    def initUI(self):

        encrypt_list = ["ECB", "CBC", "CFB", "OFB"]
        self.encrypt_mode = QComboBox(self)
        self.encrypt_mode.addItems(encrypt_list)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName('progressBar')

        self.key_input = QLineEdit(self)
        self.show_key_button = QPushButton()
        self.show_key_button.clicked.connect(self.showKey)
        self.showKey()

        self.file_name_label = QLabel(self)
        self.file_name_label.setText("No File Selected")
        self.file_name_label.setStyleSheet("font-size: 14pt")
        self.file_name_label.update()

        self.select_button = QPushButton("Select File", self)
        self.select_button.setStyleSheet("color:black")
        self.select_button.setStyleSheet("font-size: 12pt")
        self.select_button.clicked.connect(self.openFile)

        self.save_button = QPushButton("Save File", self)
        self.save_button.setStyleSheet("color:black")
        self.save_button.setStyleSheet("font-size: 12pt")
        self.save_button.clicked.connect(self.saveFile)

        self.decrypt_button = QPushButton("Decrypt", self)
        self.decrypt_button.setStyleSheet("color:black")
        self.decrypt_button.setStyleSheet("font-size: 12pt")
        self.decrypt_button.clicked.connect(lambda : self.encDecStart("dec"))

        self.encrypt_button = QPushButton("Encrypt", self)
        self.encrypt_button.setStyleSheet("color:black")
        self.encrypt_button.setStyleSheet("font-size: 12pt")
        self.encrypt_button.clicked.connect(lambda : self.encDecStart("enc"))

        self.HStack_top1 = QHBoxLayout()
        self.HStack_top1.addWidget(self.progress_bar)
        self.HStack_top1.addWidget(self.encrypt_mode)

        self.HStack_top2 = QHBoxLayout()
        self.HStack_top2.addWidget(self.file_name_label)
        self.HStack_top2.addWidget(self.select_button)
        self.HStack_top2.addWidget(self.save_button)

        self.HStack_bottom = QHBoxLayout()
        self.HStack_bottom.addWidget(self.show_key_button)
        self.HStack_bottom.addWidget(self.key_input)
        self.HStack_bottom.addWidget(self.encrypt_button)
        self.HStack_bottom.addWidget(self.decrypt_button)

        self.VStack_main = QVBoxLayout()
        self.VStack_main.addLayout(self.HStack_top1)
        self.VStack_main.addLayout(self.HStack_top2)
        self.VStack_main.addLayout(self.HStack_bottom)
        self.setLayout(self.VStack_main)

        self.filename = ""

    def encDecStart(self, type):
        mode_text = self.encrypt_mode.currentText()
        if((hasattr(self, "ed") and self.ed.isRunning()) or self.filename == ""):
            return
        in_key = self.key_input.text()
        if(in_key == ""):
            return

        self.ed = lk.CryptoThread(in_key, type, self.filename, mode=mode_text, parent=self)
        self.ed.update.connect(self.updateProgress)
        self.ed.start()

    def updateProgress(self, val):
        if(val!=self.progress_bar.value()):
            self.progress_bar.setValue(val)
            if(val==100):
                self.ed.wait()
                self.saveFile()


    def saveFile(self):
        if((hasattr(self, "ed") and self.ed.isRunning()) or not os.path.exists('out')):
            return
        file_name = QFileDialog.getSaveFileName(self, "")
        if(file_name[0] != ''):
            file_in = open('out', 'rb')
            file_out = open(file_name[0], 'wb')
            text = file_in.read()
            file_out.write(text)
            file_in.close()
            file_out.close()
            self.filename =  file_name[0]
            self.file_name_label.setText(self.filename)


    def openFile(self):
        file_name = QFileDialog.getOpenFileName(self, "")
        if(file_name[0]!= ''):
            self.filename = file_name[0]
            self.file_name_label.setText(self.filename)

    def showKey(self):
        if(self.key_input.echoMode() == QLineEdit.Password):
            icon = "../icons/hide_key_dark.png"
            type = QLineEdit.Normal
        else:
            icon = "../icons/show_key_dark.png"
            type = QLineEdit.Password

        self.show_key_button.setIcon(QIcon(QPixmap(icon)))
        self.key_input.setEchoMode(type)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
