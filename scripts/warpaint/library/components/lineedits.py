from PySide2 import QtCore, QtWidgets  # type: ignore


class FocusLineEdit(QtWidgets.QLineEdit):
    focused = QtCore.Signal()

    def focusInEvent(self, event):
        self.focused.emit()

        super().focusInEvent(event)
