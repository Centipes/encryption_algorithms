import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QMenu
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QFont

import hpc_medium as hpc

ICON_SHOW = "../icons/show_key_dark.png"
ICON_HIDE = "../icons/hide_key_dark.png"


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(100,200,300,300)
        self.setWindowTitle("HPC")
        self.Ui_Components()

    def Ui_Components(self):

        #Меню
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')
        editMenu = menubar.addMenu("Настройки")

        file_load = QAction('Загрузить файл', self)
        file_load.triggered.connect(self.load_file)

        key_load = QAction('Выбрать ключ', self)
        key_load.triggered.connect(self.read_key)

        spice_load = QAction('Выбрать соль', self)
        spice_load.triggered.connect(self.read_spice)

        enc_mode = QMenu('Режим шифрования', self)
        ecb = QAction('ECB', self)
        cbc = QAction('CBC', self)
        cfb = QAction('CFB', self)
        ofb = QAction('OFB', self)
        enc_mode.addAction(ecb)
        enc_mode.addAction(cbc)
        enc_mode.addAction(cfb)
        enc_mode.addAction(ofb)

        ecb.triggered.connect(self.ECB)
        cbc.triggered.connect(self.CBC)
        cfb.triggered.connect(self.CFB)
        ofb.triggered.connect(self.OFB)

        fileMenu.addAction(file_load)
        fileMenu.addAction(key_load)
        fileMenu.addAction(spice_load)
        editMenu.addMenu(enc_mode)

        label1= QLabel(self)
        label1.setText("HPC-Medium")
        label1.move(10,40)

        self.title_mode = "Режим шифрования: "

        self.mode_label = QLabel(self)
        self.mode_label.setText(self.title_mode + "ECB")
        self.mode_label.move(100,40)
        self.mode_label.resize(200,30)

        #----------------------------------------------------

        key_label= QLabel(self)
        key_label.setText("Ключ")
        key_label.move(10,75)

        self.key_edit = QtWidgets.QLineEdit(self)
        self.key_edit.move(70, 80)
        self.key_edit.resize(180, 20)

        self.show_key_button = QtWidgets.QPushButton(self)
        self.show_key_button.move(250, 79)
        self.show_key_button.resize(22, 22)
        self.show_key_button.clicked.connect(self.show_key)
        self.show_key()

        spice_label= QLabel(self)
        spice_label.setText("Соль")
        spice_label.move(10,105)

        self.spice_edit = QtWidgets.QLineEdit(self)
        self.spice_edit.move(70, 110)
        self.spice_edit.resize(180, 20)

        self.show_spice_button = QtWidgets.QPushButton(self)
        self.show_spice_button.move(250, 109)
        self.show_spice_button.resize(22, 22)
        self.show_spice_button.clicked.connect(self.show_spice)
        self.show_spice()

        #---------------------------------------

        enc_button = QtWidgets.QPushButton(self)
        enc_button.setText("Шифрование")
        enc_button.move(20,150)
        enc_button.clicked.connect(lambda: self.start_thread("enc"))

        dec_button = QtWidgets.QPushButton(self)
        dec_button.setText("Дешифрование")
        dec_button.move(120,150)
        dec_button.clicked.connect(lambda: self.start_thread("dec"))

        self.progressbar = QtWidgets.QProgressBar(self)
        self.progressbar.move(20, 190)
        self.progressbar.resize(240, 20)
        self.progressbar.setValue(0)

        self.title_filein = "Выбран файл: "
        self.file_in = ""
        self.file_out = ""

        self.filein_label= QLabel(self)
        self.filein_label.setText(self.title_filein)
        self.filein_label.move(20,220)
        self.filein_label.resize(500, 20)

        self.fileout_label= QLabel(self)
        self.fileout_label.move(20,240)
        self.fileout_label.resize(500, 20)

        self.msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,
                                                "Ошибка",
                                                "",
                                                QtWidgets.QMessageBox.Ok |  QtWidgets.QMessageBox.Cancel,
                                                None)
        self.mode = 'ECB'

    # Функции
    def show_key(self):
        if(self.key_edit.echoMode() == QtWidgets.QLineEdit.Password):
            icon = ICON_HIDE
            type = QtWidgets.QLineEdit.Normal
        else:
            icon = ICON_SHOW
            type = QtWidgets.QLineEdit.Password

        self.show_key_button.setIcon(QIcon(QPixmap(icon)))
        self.key_edit.setEchoMode(type)

    def show_spice(self):
        if(self.spice_edit.echoMode() == QtWidgets.QLineEdit.Password):
            icon = ICON_HIDE
            type = QtWidgets.QLineEdit.Normal
        else:
            icon = ICON_SHOW
            type = QtWidgets.QLineEdit.Password

        self.show_spice_button.setIcon(QIcon(QPixmap(icon)))
        self.spice_edit.setEchoMode(type)

    def load_file(self):
        # self.filein_label.setText(self.title_filein)
        # self.fileout_label.setText("")
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Загрузить файл")
        if fileName[0]:
            self.file_in = fileName[0]
            file_path = os.path.split(self.file_in)
            self.file_out = file_path[0] + "/" + os.path.splitext(file_path[1])[0]
            self.suffix = os.path.splitext(file_path[1])[1]
            self.filein_label.setText(self.title_filein + os.path.basename(self.file_in))

    def read_key(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Прочитать ключ", "*.txt")
        if fileName[0]:
            file_key = open(fileName[0], 'r')
            self.key_edit.setText(file_key.read())

    def read_spice(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Прочитать соль", "*.txt")
        if fileName[0]:
            file_key = open(fileName[0], 'r')
            self.spice_edit.setText(file_key.read())

    def show_message(self, text):
        self.msgBox.setText(text)
        self.msgBox.show()
        self.msgBox.exec()

    def start_thread(self, type):
        if(hasattr(self, "enc_dec") and self.enc_dec.isRunning()):
            return

        # ошибки на ключ, файл
        if (self.file_in == ""):
            self.show_message("Необходимо выбрать файл")
            return
        if(self.key_edit.text()==""):
            self.show_message("Необходимо выбрать ключ")
            return

        self.file_out += "."+type+self.suffix
        if(type=="enc"):
            self.fileout_label.setText("Зашифрованный файл: " + os.path.basename(self.file_out))
        else:
            self.fileout_label.setText("Расшифрованный файл: " + os.path.basename(self.file_out))

        self.enc_dec = hpc.CryptoThread(self.key_edit.text(), type, self.file_in, self.file_out, self.spice_edit.text(), self.mode, self)
        self.enc_dec.update.connect(self.update_progress)
        self.enc_dec.start()

    def update_progress(self, val):
        self.progressbar.setValue(val)

    def ECB(self):
        self.mode_label.setText(self.title_mode + " ECB")
        self.mode = "ECB"

    def CBC(self):
        self.mode_label.setText(self.title_mode +" CBC")
        self.mode = "CBC"

    def CFB(self):
        self.mode_label.setText(self.title_mode + " CFB")
        self.mode = "CFB"

    def OFB(self):
        self.mode_label.setText(self.title_mode + " OFB")
        self.mode = "OFB"

if __name__=="__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
