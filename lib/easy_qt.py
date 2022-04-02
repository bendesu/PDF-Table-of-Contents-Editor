from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QDialog, QGroupBox, QDialogButtonBox, QVBoxLayout
from PyQt5.QtWidgets import QFormLayout, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon

class EasyQt(QWidget):
  def __init__(self, icon_path='icon.png'):
    self.app = QApplication([])
    super().__init__()
    self.icon = QIcon(icon_path)
    self.first_file_box = True

  def input_box(self, msg = "", title = "", text = "", size = (350, 100), pos = (500,250), frameless = False):
    dlg = QInputDialog(self)
    dlg.setInputMode(QInputDialog.TextInput) 
    dlg.setLabelText(msg) 
    dlg.setWindowTitle(title)
    dlg.setTextValue(text)
    dlg.setGeometry(pos[0], pos[1], size[0], size[1])
    dlg.setWindowIcon(self.icon)
    if frameless:
      dlg.setWindowFlags(Qt.CustomizeWindowHint|Qt.FramelessWindowHint|Qt.Dialog|Qt.WindowStaysOnTopHint|Qt.Tool)
    ok = dlg.exec_()
    value = dlg.textValue()
    input = None
    if ok and value != '':
      input = str(value)
    return input

  def file_box(self, size=(650, 425), pos=(500,250), filter="Python Files (*.py);;All Files (*.*)", frameless=False, save_mode=False):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    dlg = QFileDialog(self)
    dlg.setFileMode(QFileDialog.AnyFile)
    dlg.setNameFilter(filter)
    if self.first_file_box:
      dlg.setDirectory(QDir.homePath())
      self.first_file_box = False
    dlg.setOptions(options)
    dlg.setGeometry(pos[0], pos[1], size[0], size[1])
    dlg.setWindowIcon(self.icon)
    if save_mode:
      dlg.setAcceptMode(QFileDialog.AcceptSave)
    if frameless:
      dlg.setWindowFlags(Qt.CustomizeWindowHint|Qt.FramelessWindowHint|Qt.Dialog|Qt.WindowStaysOnTopHint|Qt.Tool)
    ok = dlg.exec_()
    file_path = str(dlg.selectedFiles()[0]) if ok else None
    return file_path

  def confirm_box(self, msg = "", title = "", text = "", size = (350, 100), pos = (500,250), frameless = False):
    dlg = QMessageBox(self)
    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dlg.setDefaultButton(QMessageBox.Yes)
    dlg.setInformativeText(text)
    dlg.setText(msg)
    dlg.setWindowTitle(title)
    dlg.setGeometry(pos[0], pos[1], size[0], size[1])
    dlg.setStyleSheet("QLabel{min-width:" + f"{size[0]}" + "px;}");
    dlg.setWindowIcon(self.icon)
    if frameless:
      dlg.setWindowFlags(Qt.CustomizeWindowHint|Qt.FramelessWindowHint|Qt.Dialog|Qt.WindowStaysOnTopHint|Qt.Tool)
    input = dlg.exec_()
    if input == QMessageBox.Yes:
      input = True
    else:
      input = False
    return input

  def msg_box(self, text = "", size = (350, 100), pos = (500,250), frameless = False, title = ""):
    dlg = QMessageBox(self)
    dlg.setInformativeText(text)
    dlg.setWindowTitle(title)
    dlg.setGeometry(pos[0], pos[1], size[0], size[1])
    dlg.setStyleSheet("QLabel{min-width:" + f"{size[0]}" + "px;}");
    dlg.setWindowIcon(self.icon)
    if frameless:
      dlg.setWindowFlags(Qt.CustomizeWindowHint|Qt.FramelessWindowHint|Qt.Dialog|Qt.WindowStaysOnTopHint|Qt.Tool)
    input = dlg.exec_()
    return input

  def mega_table(self, d_title="", d_author="", d_producer="", size = (350, 100), pos = (500,250), frameless=False, w_title=""):
    dlg = QDialog(self)
    form = QGroupBox("Meta Data:")
    layout = QFormLayout()
    title = QLineEdit(text=d_title)
    author = QLineEdit(text=d_author)
    producer = QLineEdit(text=d_producer)
    layout.addRow(QLabel("Title:"), title)
    layout.addRow(QLabel("Author:"), author)
    layout.addRow(QLabel("Producer:"), producer)
    form.setLayout(layout)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dlg.accept)
    button_box.rejected.connect(dlg.reject)
    main_layout = QVBoxLayout()
    main_layout.addWidget(form)
    main_layout.addWidget(button_box)
    dlg.setLayout(main_layout)
    dlg.setWindowTitle(w_title)
    dlg.setWindowIcon(self.icon)
    dlg.setGeometry(pos[0], pos[1], size[0], size[1])
    if frameless:
      dlg.setWindowFlags(Qt.CustomizeWindowHint|Qt.FramelessWindowHint|Qt.Dialog|Qt.WindowStaysOnTopHint|Qt.Tool)
    ok = dlg.exec_()
    if ok:
      return [title.text(), author.text(), producer.text()]
    return None
      