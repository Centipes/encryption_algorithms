style = """

QLineEdit {
    background-color: white;
    border-color: grey;
    border: none;
}

QProgressBar {
    min-height: 14px;
    max-height: 14px;
    border: solid grey;
    background-color: #7c7174;
    color: white;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #c14aff;
}

QRadioButton {
    color: white;
}

#system {
    color : white;
}

#main {
    background-color: #E4E2E3;
}
#cipher{
    background-color: #443748;
}
QLabel {
    color: white;

}
#fileinfo_label {
    background-color: #a1989a;
}
#show_button {
    border: none;
    background-color: #a1989a;
}
#show_button:hover{
    background-color: white;
}

#stop_button{
    opacity: 50;
    background-color: white;
}

#enc_button {
    opacity: 50;
    background-color: white;
    border-top-left-radius: 15px;
    border-bottom-left-radius: 15px;
}
#dec_button {
    opacity: 50;
    background-color: white;
    border-top-right-radius: 15px;
    border-bottom-right-radius: 15px;
}

#action_key_button {
    background-color:transparent;
    border:none;
}
#action_key_button:hover {
    background-color: #a1989a;
}

QApplication{
    background-color: #E4E2E3;
}

"""
combobox_style = """

QComboBox{
    border: 1px solid #c14aff;
    color: white;
    background-color: transparent;
    background-repeat: no repeat;
}
QListView{
    color: white;
}
QComboBox QAbstractItemView {
    background-color: #443748;
    selection-background-color: #4dc14aff;
    border: 1px solid #c14aff;
    padding-right: 2px;
    padding-left: 2px;
    padding-top: 2px;
    padding-bottom: 2px;
}

"""

tree_style = """

QWidget{
    background:#E4E2E3;
}
QTreeView {
    background:#E4E2E3;
    color: black;
    border:none;
}


QScrollBar:vertical {
    border: none;
    background: white;
    width: 8px;
    margin: 0 2 0 2;
    border-radius: 0px;
}
QScrollBar::handle:vertical {
    background: #CDCBCC;
    border-radius: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: #7c7174;
}
QScrollBar::sub-line:vertical {
    border: none;
}
QScrollBar::add-line:vertical {
    border: none;
}
QPushButton{
    background-color: #4D7c7174;
    border: none;
    text-align: left;
    padding: 6px;
}

"""
