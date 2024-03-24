#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore

from warpaint.library.components import layouts, buttons, tiles, lineedits, responses
from warpaint.model import strokes, colours


class StrokesGroup(QtWidgets.QWidget):
    def __init__(self, regions, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regions = regions
        self.settings = settings

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.group = QtWidgets.QButtonGroup(exclusive=True)
        self.add_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:add.svg"), toolTip="Add Region")
        self.delete_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:delete.svg"), toolTip="Delete Region")
        self.delete_button.setProperty("state", "error_hover")

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self, contentsMargins=QtCore.QMargins(0, 0, 0, 0), spacing=0)

        self.container = QtWidgets.QVBoxLayout(contentsMargins=QtCore.QMargins(0, 0, 0, 0), spacing=6)
        self.scroll_area = layouts.to_scroll_area(self.container)
        main_layout.addWidget(self.scroll_area)

        buttons_layout = QtWidgets.QHBoxLayout(spacing=6)
        buttons_layout.addWidget(layouts.horizontal_divider(expand=True))
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.delete_button)
        main_layout.addLayout(buttons_layout)

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.add_button.clicked.connect(self.on_add_stroke)
        self.delete_button.clicked.connect(self.on_remove_stroke)

        self.regions.region_changed.connect(self.on_region_changed)
        self.regions.region_renamed.connect(self.on_region_renamed)
        self.regions.region_deleted.connect(self.on_region_deleted)

    def on_add_stroke(self):
        all_stroke_edits = list(self.all_strokes())

        colour = colours.get_colour_by_index(len(all_stroke_edits))
        current_region = self.regions.current_region()

        if current_region:
            stroke_edit = self.append_stroke("", colour=colour, region=current_region)
            stroke_edit.focus()

            self.scroll_to_bottom()

    def on_remove_stroke(self):
        stroke_edit = self.current_stroke()

        if not stroke_edit:
            return

        if len(stroke_edit.model.polygons) > 0:
            if not responses.question(self, "Remove Stroke", "This stroke has polygons selected. Are you sure you want to remove it?"):
                return

        # -- Delete.
        stroke_edit.delete()

        # -- Select Next Visible Stroke.
        for stroke_edit in reversed(list(self.all_strokes(visible_only=True))):
            stroke_edit.focus()
            break

    def on_region_changed(self, region):
        layouts.clear_radio_group(self.group)
        self.add_button.setEnabled(bool(region))

        for stroke_edit in self.all_strokes():
            if not region or stroke_edit.model.region == region:  # None/"" == All.
                stroke_edit.model.to_highlight()
                stroke_edit.setVisible(True)
            else:
                stroke_edit.model.to_fade()
                stroke_edit.setVisible(False)

    def on_region_renamed(self, prev_region, new_region):
        for stroke_edit in self.all_strokes(prev_region):
            stroke_edit.model.region = new_region

    def on_region_deleted(self, region):
        for stroke_edit in self.all_strokes(region):
            stroke_edit.delete()

    def update_placeholder(self):
        for stroke_edit in self.all_strokes():
            stroke_edit.set_placeholder()

    # • ───────────────────────────
    # • ──── Utils. ────

    def append_stroke(self, name, colour, region, polygons=None):
        stroke = strokes.Stroke(name, colour=colour, region=region, polygons=polygons or set(), settings=self.settings)
        stroke_edit = StrokeEdit(stroke, self.regions)

        self.group.addButton(stroke_edit.radio_button)
        self.container.addWidget(stroke_edit)
        return stroke_edit

    def scroll_to_bottom(self):
        QtCore.QTimer.singleShot(0, partial(layouts.scroll_to_bottom, self.scroll_area))

    def clear(self):
        for stroke_edit in list(self.all_strokes()):
            stroke_edit.delete()

    def current_stroke(self):
        active_radio = self.group.checkedButton()
        return active_radio.parent() if active_radio else None

    def all_strokes(self, region=None, visible_only=False):
        for index in range(self.container.count()):
            item = self.container.itemAt(index).widget()

            if isinstance(item, StrokeEdit):
                if region is None or item.model.region == region:  # None == All.
                    if not visible_only or item.isVisible():
                        yield item

    # • ───────────────────────────
    # • ──── IO. ────

    def import_data(self, mesh, data):
        self.clear()

        stroke_edit = None
        colours_map = {colour.name: colour for colour in colours.COLOURS}

        for stroke, values in data.items():
            colour = colours_map.get(values["colour_name"], None) or colours.MISSING_COLOUR
            polygons = set([f"{mesh}.f[{index}]" for index in values["indices"]])

            stroke_edit = self.append_stroke(stroke, colour=colour, region=values["region"], polygons=polygons)

        if stroke_edit:
            stroke_edit.focus()
            self.scroll_to_bottom()


class StrokeEdit(QtWidgets.QWidget):
    def __init__(self, stroke, regions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stroke = stroke
        self.regions = regions

        self.setup_widgets()
        self.setup_layouts()

        self.populate()
        self.bind_connections()

    @property
    def model(self):
        return self._stroke

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.radio_button = QtWidgets.QRadioButton()
        self.name_edit = lineedits.FocusLineEdit()

        self.select_button = buttons.DynamicToolTipPushButton(icon=QtGui.QIcon("icons:select_all.svg"), toolTip="Select Polygons")

        self.colour_button = buttons.RightClickToolButton(toolTip="Change Colour")
        self.colour_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.colour_button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

        self.colour_menu = QtWidgets.QMenu(self)
        self.colour_button.setMenu(self.colour_menu)

        self.region_button = QtWidgets.QToolButton(icon=QtGui.QIcon("icons:world.svg"), toolTip="Change Region")
        self.region_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.region_menu = QtWidgets.QMenu(self)
        self.region_button.setMenu(self.region_menu)

    def setup_layouts(self):
        main_layout = QtWidgets.QHBoxLayout(self, contentsMargins=QtCore.QMargins(6, 6, 6, 6), spacing=6)

        main_layout.addWidget(self.radio_button)
        main_layout.addWidget(self.name_edit)

        side_layout = QtWidgets.QHBoxLayout()
        side_layout.addWidget(self.select_button)
        side_layout.addWidget(self.colour_button)
        side_layout.addWidget(self.region_button)
        main_layout.addLayout(side_layout)

    # • ———————————————————————————
    # • ———— Populate. ————

    def populate(self):
        self.name_edit.setText(self.model.name)
        self.set_colour()

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.name_edit.textChanged.connect(self.set_name)
        self.name_edit.focused.connect(self.radio_button.click)

        self.colour_button.right_clicked.connect(self.randomize_colour)
        self.colour_menu.aboutToShow.connect(self.generate_colour_menu)
        self.region_menu.aboutToShow.connect(self.generate_region_menu)

        self.select_button.aboutToShow.connect(self.set_tooltip)
        self.select_button.clicked.connect(lambda: self.model.select_polygons())

    def set_name(self, name):
        self.model.name = name

    def generate_colour_menu(self):
        self.colour_menu.clear()

        for colour in colours.get_colours(only_active=True):
            colour_icon = tiles.ColourTile.icon(colour=colour.highlight_RGB())

            action = QtWidgets.QAction(colour.alias or colour.name, self.colour_menu, icon=colour_icon)
            action.triggered.connect(partial(self.set_colour, colour))
            self.colour_menu.addAction(action)

    def generate_region_menu(self):
        self.region_menu.clear()

        for region in self.regions.all_regions():
            action = QtWidgets.QAction(region, self.region_menu)
            action.triggered.connect(partial(self.on_region_change, region))
            self.region_menu.addAction(action)

    def set_colour(self, colour=None):
        if colour:
            self.model.colour = colour

        colour_icon = tiles.ColourTile.icon(colour=self.model.colour.highlight_RGB())

        self.colour_button.setIcon(colour_icon)
        self.colour_button.setToolTip(self.model.colour.description)
        self.set_placeholder()
        self.model.repaint()

    def set_placeholder(self):
        self.name_edit.setPlaceholderText(f"{self.model.colour.alias or self.model.colour.name} Area Stroke Name")

    def randomize_colour(self):
        random_colour = colours.get_random_colour()
        self.set_colour(random_colour)

    def set_tooltip(self):
        count = len(self.model.polygons)
        self.select_button.setToolTip(f"Select {count} polygon(s).")

    def on_region_change(self, region):
        if region == self.model.region:
            return

        self.model.region = region
        self.regions.set_region(region)
        self.focus()

    # • ──────────────────────────
    # • ──── Utils. ────

    def focus(self):
        self.name_edit.setFocus()
        self.radio_button.click()

    def delete(self):
        self.model.decolourize()

        self.setParent(None)
        self.deleteLater()
