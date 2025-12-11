#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from warpaint.qt import QtWidgets, QtCore


class FocusLineEdit(QtWidgets.QLineEdit):
    focused = QtCore.Signal()

    def focusInEvent(self, event):
        self.focused.emit()

        super().focusInEvent(event)
