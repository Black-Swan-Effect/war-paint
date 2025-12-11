#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from warpaint.qt import QtWidgets, QtCore, QtGui

from warpaint.library.components import layouts
from warpaint.partials.shades_ui import ShadesUI


class PreferencesUI(QtWidgets.QWidget):
    updated = QtCore.Signal()

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.shades = ShadesUI(self.settings)

        self.save_button = QtWidgets.QPushButton("Save Preferences", icon=QtGui.QIcon("icons:save.svg"))
        self.save_button.setProperty("default_text", "Update")

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.shades)

        main_layout.addStretch()
        main_layout.addWidget(layouts.horizontal_divider())
        main_layout.addWidget(self.save_button)

    # • ———————————————————————————
    # • ———— Populate. ————

    def populate(self):
        self.shades.populate()

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.save_button.clicked.connect(self.on_update)

    def on_update(self):
        self.shades.save()
        self.updated.emit()

        self.save_button.setText("Changes Saved!")
        default_text = self.save_button.property("default_text")
        QtCore.QTimer.singleShot(2000, lambda: self.save_button.setText(default_text))
