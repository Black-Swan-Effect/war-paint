import logging
from PySide2 import QtWidgets


log = logging.getLogger(__name__)


def clipboard_copy(string):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText(string)
