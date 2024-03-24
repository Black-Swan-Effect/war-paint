#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from contextlib import contextmanager
from PySide2 import QtCore, QtWidgets  # type: ignore

from warpaint.library.setup import template
from warpaint.model.settings import Settings
from warpaint.tabs import blend_ui, files_ui, paint_ui, alias_ui, preferences_ui


class WarPaintUI(template.BaseTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.__class__.__name__.replace("UI", ""))
        self.setObjectName(self.__class__.__name__)
        self.setMinimumSize(700, 330)

        self.settings = Settings()

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)

        self.paint = paint_ui.PainterUI(self.settings)
        self.tabs.addTab(self.paint, "Paint")

        self.blend = blend_ui.BlenderUI(self.settings)
        self.tabs.addTab(self.blend, "Blend")

        self.files = files_ui.FilesUI(self.settings, self.loading, self.paint)
        self.tabs.addTab(self.files, "Files")

        self.alias = alias_ui.AliasUI(self.settings)
        self.tabs.addTab(self.alias, "Colours")

        self.preferences = preferences_ui.PreferencesUI(self.settings)
        self.tabs.addTab(self.preferences, "Preferences")

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self, spacing=0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.tabs)

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.raise_window.connect(self.files.populate)
        self.raise_window.connect(self.paint.populate)
        self.raise_window.connect(self.preferences.populate)
        self.raise_window.connect(self.alias.populate)

        self.alias.updated.connect(self.paint.on_alias_change)
        self.preferences.updated.connect(self.paint.repaint)
        self.preferences.updated.connect(self.alias.repaint)

    @contextmanager
    def loading(self):
        progress = QtWidgets.QProgressDialog("Processing..", None, 0, 0, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        QtCore.QCoreApplication.processEvents()

        yield
        progress.close()
