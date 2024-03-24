#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2 import QtCore, QtWidgets  # type: ignore

from warpaint.library.components import tiles, layouts
from warpaint.library.components.signals import DisableSignals
from warpaint.model import colours


class ShadesUI(QtWidgets.QWidget):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.highlight_tile = tiles.ColourTile(size=42)
        self.highlight_tile.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.highlight_shade_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, minimum=1, maximum=9, toolTip="Adjust the shade.")
        self.highlight_saturation_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, minimum=10, maximum=100, toolTip="Adjust the saturation.")

        self.fade_tile = tiles.ColourTile(size=42)
        self.fade_tile.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.fade_shade_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, minimum=1, maximum=9, toolTip="Adjust the shade.")
        self.fade_saturation_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, minimum=10, maximum=100, toolTip="Adjust the saturation.")

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self, contentsMargins=QtCore.QMargins(0, 0, 0, 0), spacing=6)

        highlight_layout = QtWidgets.QVBoxLayout(spacing=12)
        highlight_layout.addWidget(self.highlight_tile)
        highlight_layout.addLayout(layouts.wrap_label("L:", self.highlight_shade_slider, horizontal=True))
        highlight_layout.addLayout(layouts.wrap_label("S:", self.highlight_saturation_slider, horizontal=True))
        main_layout.addWidget(layouts.to_group(highlight_layout, "Highlight Colour"))

        main_layout.addWidget(layouts.horizontal_divider())

        fade_layout = QtWidgets.QVBoxLayout(spacing=12)
        fade_layout.addWidget(self.fade_tile)
        fade_layout.addLayout(layouts.wrap_label("L:", self.fade_shade_slider, horizontal=True))
        fade_layout.addLayout(layouts.wrap_label("S:", self.fade_saturation_slider, horizontal=True))
        main_layout.addWidget(layouts.to_group(fade_layout, "Fade Colour"))

    # • ———————————————————————————
    # • ———— Populate. ————

    def populate(self):
        highlight_shade = int(self.settings["highlight_shade"] or colours.DEFAULT_SHADE)
        highlight_saturation = float(self.settings["highlight_saturation"] or colours.DEFAULT_SATURATION)

        with DisableSignals(self.highlight_shade_slider, self.highlight_saturation_slider):
            self.highlight_shade_slider.setValue(highlight_shade)
            self.highlight_saturation_slider.setValue(int(highlight_saturation * 100))

        fade_shade = int(self.settings["fade_shade"] or colours.DEFAULT_SHADE)
        fade_saturation = float(self.settings["fade_saturation"] or colours.DEFAULT_SATURATION)

        with DisableSignals(self.fade_shade_slider, self.fade_saturation_slider):
            self.fade_shade_slider.setValue(fade_shade)
            self.fade_saturation_slider.setValue(int(fade_saturation * 100))

        self.repaint()

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.highlight_shade_slider.valueChanged.connect(self.on_highlight_change)
        self.highlight_saturation_slider.valueChanged.connect(self.on_highlight_change)

        self.fade_shade_slider.valueChanged.connect(self.on_fade_change)
        self.fade_saturation_slider.valueChanged.connect(self.on_fade_change)

        self.highlight_tile.clicked.connect(self.repaint)
        self.fade_tile.clicked.connect(self.repaint)

    def on_highlight_change(self):
        shade = self.highlight_shade_slider.value()
        saturation = self.highlight_saturation_slider.value()

        colour = self.colour.highlight_RGB(shade, saturation / 100.0)
        self.highlight_tile.set_colour(colour)

    def on_fade_change(self):
        shade = self.fade_shade_slider.value()
        saturation = self.fade_saturation_slider.value()

        colour = self.colour.fade_RGB(shade, saturation / 100.0)
        self.fade_tile.set_colour(colour)

    def repaint(self):
        self.colour = colours.get_random_colour()
        self.on_highlight_change()
        self.on_fade_change()

    # • ———————————————————————————
    # • ———— Utils. ————

    def save(self):
        self.settings["highlight_shade"] = str(self.highlight_shade_slider.value())
        self.settings["highlight_saturation"] = str(self.highlight_saturation_slider.value() / 100)

        self.settings["fade_shade"] = str(self.fade_shade_slider.value())
        self.settings["fade_saturation"] = str(self.fade_saturation_slider.value() / 100)
