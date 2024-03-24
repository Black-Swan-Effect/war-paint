#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2 import QtCore, QtWidgets, QtGui  # type: ignore


SIZE = 42
HANDLE_RADIUS_RATIO = 0.25
BAR_HEIGHT_RATIO = 0.25

BAR_COLOUR = "#22282A"
HANDLE_COLOUR = "#d4d4d8"
CHECKED_COLOUR = "#0ea5e9"

BAR_BRUSH = QtGui.QBrush(QtGui.QColor(BAR_COLOUR))
BAR_BRUSH_CHECKED = QtGui.QBrush(QtGui.QColor(CHECKED_COLOUR).lighter())
HANDLE_BRUSH = QtGui.QBrush(QtGui.QColor(HANDLE_COLOUR))
HANDLE_BRUSH_CHECKED = QtGui.QBrush(QtGui.QColor(CHECKED_COLOUR))


class Toggle(QtWidgets.QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(SIZE, SIZE)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setContentsMargins(3, 0, 3, 0)

    def hitButton(self, position):
        return self.contentsRect().contains(position)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        content_rect = self.contentsRect()
        handle_radius = round(HANDLE_RADIUS_RATIO * content_rect.height())

        bar_rect = QtCore.QRectF(0, 0, content_rect.width() - handle_radius, BAR_HEIGHT_RATIO * content_rect.height())
        bar_rect.moveCenter(content_rect.center())
        rounding = bar_rect.height() / 2

        trail_length = content_rect.width() - 2 * handle_radius
        handle_position = content_rect.x() + handle_radius + trail_length * int(self.isChecked())

        painter.setBrush(BAR_BRUSH_CHECKED if self.isChecked() else BAR_BRUSH)
        painter.drawRoundedRect(bar_rect, rounding, rounding)

        painter.setBrush(HANDLE_BRUSH_CHECKED if self.isChecked() else HANDLE_BRUSH)
        painter.drawEllipse(QtCore.QPointF(handle_position, bar_rect.center().y()), handle_radius, handle_radius)
