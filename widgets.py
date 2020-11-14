from PyQt5 import QtWidgets


class VContainer(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(VContainer, self).__init__(*args, **kwargs)
        self.setLayout(QtWidgets.QVBoxLayout())

    def addWidget(self, w):
        self.layout().addWidget(w)


class HContainer(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(HContainer, self).__init__(*args, **kwargs)
        self.setLayout(QtWidgets.QHBoxLayout())

    def addWidget(self, w):
        self.layout().addWidget(w)


class LogWrite(QtWidgets.QTextEdit):
    def addMessage(self, text):
        current = self.toPlainText()
        self.setText(current + text + "\n")
        vs = self.verticalScrollBar()
        vs.setValue(vs.maximum())
