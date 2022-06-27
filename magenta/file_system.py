import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets

DIR_ICON_PATH = '../icons/dir.png'
FILE_ICON_PATH = '../icons/file.png'

class FileSystemModel(QtWidgets.QFileSystemModel):

    def __init__(self, parent):
        QtWidgets.QFileSystemModel.__init__(self)
        self.path = QtCore.QDir.currentPath()
        self.button = QtWidgets.QPushButton(self.path, parent)
        self.button.clicked.connect(self.change_directory)
        self.button.resize(parent.width()-2,31)
        self.parent = parent

    def change_directory(self):
        self.path = os.path.split(self.path)[0]
        self.parent.setRootIndex(self.index(self.path))
        self.button.setText(self.path)

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if (orientation == QtCore.Qt.Horizontal):
            return None

        return "{}".format(section)

    def data(self, index, role):
        column = index.column()
        if(role == QtCore.Qt.DecorationRole):

            name = index.data()
            info = QtCore.QFileInfo(name)

            if(info.isDir()):
                return QtGui.QPixmap(DIR_ICON_PATH)
            elif(column == 0):
                return QtGui.QPixmap(FILE_ICON_PATH)
        if(role==QtCore.Qt.TextAlignmentRole):
            if(column == 2):
                return QtCore.Qt.AlignRight

        if role == QtCore.Qt.ToolTipRole:
            return self.fileInfo(index).filePath()

        return QtWidgets.QFileSystemModel.data(self, index, role)

class FileSystemTree(QtWidgets.QTreeView):

    file_is_changed = QtCore.pyqtSignal()

    def __init__(self):
        super(FileSystemTree, self).__init__()
        self.filename = ""
        self.filetype = ""
        self.filesize = ""
        self.filedate = ""
        self.initUI()
        self.clicked.connect(self.onClicked)


    def currentChanged(self, c, p):

        fileinfo = self.model().fileInfo(c)
        self.filepath = self.model().fileInfo(c).filePath()
        self.filename = os.path.splitext(str(fileinfo.fileName()))[0]
        self.filetype = str(fileinfo.suffix())

        try:
            self.filesize = self.convert_bytes(os.path.getsize(str(self.filepath)))
        except:
            self.filesize = ""

        self.filedate = fileinfo.lastModified().date().toString('yyyy/MM/dd')

        if(c.isValid()):
            self.scrollTo(c)

        self.file_is_changed.emit()

    def onClicked(self, index):
        path = self.sender().model().filePath(index)
        info = QtCore.QFileInfo(path)
        if(info.isDir()):
            self.setRootIndex(self.source_model.index(path))
            self.source_model.path = path
            self.source_model.button.setText(path)

    def convert_bytes(self, size):
        size_name = ("B", "KB", "MB", "GB", "TB")
        for i in range(4):
            if(size<1024):
                return "%.2f"%(size) + size_name[i]
            size/=1024
        return "%.2f"%(size) + size_name[4]

    def initUI(self):
        self.resize(500, 400)
        self.source_model = FileSystemModel(self)
        self.source_model.setOption(QtWidgets.QFileSystemModel.DontUseCustomDirectoryIcons)
        self.source_model.setRootPath('')
        self.setModel(self.source_model)
        self.setRootIndex(self.source_model.index(QtCore.QDir.currentPath()))
        self.hideColumn(3)
        self.hideColumn(2)
        self.hideColumn(1)
