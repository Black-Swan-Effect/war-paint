#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from warpaint.qt import QtWidgets, QtCore, QtGui


class ColourTile(QtWidgets.QWidget):
    clicked = QtCore.Signal(object)

    def __init__(self, colour=None, size=42, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        self.set_colour(colour)

        self._size = size

    def set_colour(self, colour):
        colour = colour or "#000000"
        colour = QtGui.QColor(*colour) if isinstance(colour, (list, tuple)) else QtGui.QColor(colour)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), colour)
        self.setPalette(palette)

    def sizeHint(self):
        return QtCore.QSize(self._size, self._size)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(event)
            return event.accept()

        super(ColourTile, self).mousePressEvent(event)

    @staticmethod
    def icon(colour, size=42):
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtGui.QColor(*colour))
        return QtGui.QIcon(pixmap)
