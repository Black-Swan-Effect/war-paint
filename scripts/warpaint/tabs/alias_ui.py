#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from warpaint.qt import QtWidgets, QtCore, QtGui

from warpaint.library.components import tiles, toggle, layouts
from warpaint.model import colours


class AliasRow(QtWidgets.QWidget):
    def __init__(self, first, colour, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first = first
        self._colour = colour
        self.settings = settings

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    @property
    def model(self):
        return self._colour

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.active_toggle = toggle.Toggle(checked=self.model.is_active)
        self.tile = tiles.ColourTile(colour=self.model.highlight_RGB(), size=24)
        self.name = QtWidgets.QLineEdit(self.model.alias)
        self.name.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        self.description = QtWidgets.QLineEdit(self.model.description)
        self.description.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self, contentsMargins=QtCore.QMargins(0, 0, 0, 0), spacing=6)

        edit_layout = QtWidgets.QHBoxLayout()
        edit_layout.addLayout(layouts.wrap_label("", self.tile))
        edit_layout.addLayout(layouts.wrap_label("", self.active_toggle))
        edit_layout.addLayout(layouts.wrap_label("Alias" if self.first else "", self.name))
        edit_layout.addLayout(layouts.wrap_label("Description" if self.first else "", self.description))

        main_layout.addLayout(edit_layout)

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.active_toggle.toggled.connect(self.on_active_toggle)
        self.name.textChanged.connect(self.on_name_changed)
        self.description.textChanged.connect(self.on_description_changed)

    def on_active_toggle(self):
        self.model.is_active = self.active_toggle.isChecked()

    def on_name_changed(self):
        self.model.alias = self.name.text()

    def on_description_changed(self):
        self.model.description = self.description.text()

    # • ———————————————————————————
    # • ———— Utils. ————

    def repaint(self):
        self.tile.set_colour(self.model.highlight_RGB())


class AliasUI(QtWidgets.QWidget):
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
        self.save_button = QtWidgets.QPushButton("Save Preferences", icon=QtGui.QIcon("icons:save.svg"))
        self.save_button.setProperty("default_text", "Update")

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        self.container = QtWidgets.QVBoxLayout(contentsMargins=QtCore.QMargins(0, 0, 0, 0), spacing=6)
        self.scroll_area = layouts.to_scroll_area(self.container)
        main_layout.addWidget(self.scroll_area)

        main_layout.addWidget(layouts.horizontal_divider())
        main_layout.addWidget(self.save_button)

    def populate(self):
        layouts.clear_layout(self.container)

        for index, colour in enumerate(colours.COLOURS):
            row = AliasRow(index == 0, colour, self.settings)
            self.container.addWidget(row)

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.save_button.clicked.connect(self.on_update)

    def on_update(self):
        colours.save_colours()
        self.updated.emit()

        self.save_button.setText("Changes Saved!")
        default_text = self.save_button.property("default_text")
        QtCore.QTimer.singleShot(2000, lambda: self.save_button.setText(default_text))

    # • ———————————————————————————
    # • ———— Utils. ————

    def all_rows(self):
        for index in range(self.container.count()):
            item = self.container.itemAt(index).widget()

            if isinstance(item, AliasRow):
                yield item

    def repaint(self):
        for row in self.all_rows():
            row.repaint()
