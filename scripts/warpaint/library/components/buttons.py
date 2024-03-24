#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2 import QtCore, QtWidgets  # type: ignore


class RightClickToolButton(QtWidgets.QToolButton):
    right_clicked = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        super(RightClickToolButton, self).__init__(parent, *args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.right_clicked.emit()
            return event.accept()

        super(RightClickToolButton, self).mousePressEvent(event)


class DynamicToolTipPushButton(QtWidgets.QPushButton):
    aboutToShow = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(DynamicToolTipPushButton, self).__init__(*args, **kwargs)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ToolTip:
            self.aboutToShow.emit()

        return super(DynamicToolTipPushButton, self).eventFilter(obj, event)
