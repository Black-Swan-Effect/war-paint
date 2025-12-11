#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from warpaint.qt import QtWidgets, QtCore, QtGui

from warpaint.library.components import responses
from warpaint.library.components.signals import DisableSignals


class Regions(QtWidgets.QWidget):
    region_changed = QtCore.Signal(None or str)
    region_renamed = QtCore.Signal(str, str)
    region_deleted = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.regions_dropdown = QtWidgets.QComboBox()
        self.regions_dropdown.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.regions_dropdown.addItems(["All", "anonymous"])
        self.regions_dropdown.setCurrentIndex(1)

        self.add_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:add.svg"), toolTip="Add Region")
        self.edit_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:edit.svg"), toolTip="Edit Region")
        self.delete_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:delete.svg"), toolTip="Delete Region")
        self.delete_button.setProperty("state", "error_hover")

    def setup_layouts(self):
        main_layout = QtWidgets.QHBoxLayout(self, contentsMargins=QtCore.QMargins(0, 0, 0, 0), spacing=6)

        main_layout.addWidget(self.regions_dropdown)

        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.edit_button)
        main_layout.addWidget(self.delete_button)

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.regions_dropdown.currentIndexChanged.connect(self.on_regions_change)

        self.add_button.clicked.connect(self.add_region)
        self.edit_button.clicked.connect(self.edit_region)
        self.delete_button.clicked.connect(self.delete_region)

    def on_regions_change(self, index):
        self.edit_button.setEnabled(index != 0)
        self.delete_button.setEnabled(index != 0)

        self.region_changed.emit(self.current_region())

    def add_region(self):
        region, valid = QtWidgets.QInputDialog.getText(self, "New Region", "Enter Name:")

        if valid and region:
            self.regions_dropdown.addItem(region)
            self.regions_dropdown.setCurrentIndex(self.regions_dropdown.count() - 1)

    def edit_region(self):
        prev_region, index = self.regions_dropdown.currentText(), self.regions_dropdown.currentIndex()
        new_region, valid = QtWidgets.QInputDialog.getText(self, "Edit Name", "New Name:", text=prev_region)

        if valid and new_region not in self.all_regions():
            self.region_renamed.emit(prev_region, new_region)
            self.regions_dropdown.setItemText(index, new_region)

    def delete_region(self):
        current_index = self.regions_dropdown.currentIndex()
        current_region = self.regions_dropdown.currentText()

        if responses.question(self, "Delete Region", f"Are you sure you want to delete the region '{current_region}'?"):
            self.region_deleted.emit(current_region)
            self.regions_dropdown.removeItem(current_index)

    # • ———————————————————————————
    # • ———— Query. ————

    def set_region(self, region):
        index = self.regions_dropdown.findText(region)
        self.regions_dropdown.setCurrentIndex(index)

    def current_region(self):
        region = self.regions_dropdown.currentText()
        return region if region != "All" else None

    def all_regions(self):
        return [self.regions_dropdown.itemText(index) for index in range(1, self.regions_dropdown.count())]

    def clear(self):
        self.regions_dropdown.clear()
        self.regions_dropdown.addItems(["All"])

    def import_data(self, data):
        with DisableSignals(self.regions_dropdown):
            self.clear()

            regions = set(value["region"] for value in data.values())
            self.regions_dropdown.addItems(list(regions))

        self.on_regions_change(0)
