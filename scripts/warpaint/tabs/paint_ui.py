from maya import cmds
from PySide2 import QtGui, QtCore, QtWidgets  # type: ignore

from warpaint.library import api
from warpaint.library.components import layouts, responses
from warpaint.partials.regions_ui import Regions
from warpaint.partials.strokes_ui import StrokesGroup


class PainterUI(QtWidgets.QWidget):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.is_saved = True

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.mesh = QtWidgets.QLabel("...")
        self.mesh.setProperty("default_text", "...")
        self.mesh.setStyleSheet("font-style: italic;")

        self.regions = Regions()

        self.strokes_group = StrokesGroup(regions=self.regions, settings=self.settings)
        self.strokes_group.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.paint_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:brush.svg"))
        self.paint_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.mode_group = QtWidgets.QButtonGroup(exclusive=True)

        self.replace_radio = QtWidgets.QRadioButton(icon=QtGui.QIcon("icons:cursor.svg"))
        self.mode_group.addButton(self.replace_radio)

        self.append_radio = QtWidgets.QRadioButton(checked=True, icon=QtGui.QIcon("icons:cursor_plus.svg"))
        self.mode_group.addButton(self.append_radio)

        self.remove_radio = QtWidgets.QRadioButton(icon=QtGui.QIcon("icons:cursor_minus.svg"))
        self.mode_group.addButton(self.remove_radio)

        self.clean_up_button = QtWidgets.QPushButton("restore", icon=QtGui.QIcon("icons:revert.svg"))
        self.clean_up_button.setProperty("state", "error_hover")
        size = self.strokes_group.add_button.sizeHint() + self.strokes_group.delete_button.sizeHint()

        self.clean_up_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.clean_up_button.setFixedWidth(size.width() + 6)

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.mesh, alignment=QtCore.Qt.AlignCenter)
        main_layout.addWidget(layouts.horizontal_divider())

        regions_layout = QtWidgets.QHBoxLayout()
        regions_layout.addWidget(self.regions)
        group = layouts.to_group(regions_layout, "Regions")
        main_layout.addWidget(group)

        main_layout.addWidget(self.strokes_group)

        radio_layout = QtWidgets.QHBoxLayout(spacing=24)
        radio_layout.addWidget(self.replace_radio)
        radio_layout.addWidget(self.append_radio)
        radio_layout.addWidget(self.remove_radio)

        actions_layout = QtWidgets.QHBoxLayout(spacing=6)
        actions_layout.addLayout(radio_layout)
        actions_layout.addWidget(self.paint_button)
        actions_layout.addWidget(self.clean_up_button)

        main_layout.addLayout(actions_layout)

    # • ———————————————————————————
    # • ———— Populate. ————

    def populate(self):
        if not list(self.strokes_group.all_strokes()):
            self.strokes_group.on_add_stroke()

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.regions.region_renamed.connect(self.dirty)
        self.regions.region_deleted.connect(self.dirty)
        self.paint_button.clicked.connect(self.on_paint)
        self.clean_up_button.clicked.connect(self.cleanup)

    def dirty(self):
        self.is_saved = False

    def on_paint(self):
        mode = self.mode_group.checkedButton()
        stroke = self.strokes_group.current_stroke()

        selection = cmds.filterExpand(selectionMask=34)
        polygons = set(self._validate_selection(selection))

        if polygons:
            if mode == self.remove_radio:
                self._remove_paint(polygons)

            if not stroke:
                responses.modal(self, False, "No Stroke", "No stroke selected.")
                return

            if mode == self.append_radio and stroke:
                self._append_paint(polygons, stroke)
            elif mode == self.replace_radio and stroke:
                self._replace_paint(polygons, stroke)

        self.dirty()

    # • ———————————————————————————
    # • ———— Paint. ————

    def _validate_selection(self, selection):
        if not selection:
            return

        mesh = self.mesh.text()

        if not mesh or mesh == self.mesh.property("default_text"):
            mesh = api.get_node(selection[0])
            self.mesh.setText(mesh)

        for item in selection:
            if mesh == api.get_node(item):
                yield item

    def _remove_paint(self, polygons):
        for stroke in self.strokes_group.all_strokes():
            stroke.model.remove_polygons(polygons)

    def _append_paint(self, polygons, stroke):
        for other_stroke in filter(lambda x: x != stroke, self.strokes_group.all_strokes()):
            other_stroke.model.remove_polygons(polygons)

        stroke.model.add_polygons(polygons)

    def _replace_paint(self, polygons, stroke):
        for other_stroke in filter(lambda x: x != stroke, self.strokes_group.all_strokes()):
            other_stroke.model.remove_polygons(polygons)

        stroke.model.set_polygons(polygons)

    def on_alias_change(self):
        self.strokes_group.update_placeholder()

    # • ———————————————————————————
    # • ———— IO. ————

    def import_data(self, mesh, data):
        self.mesh.setText(mesh)
        self.regions.import_data(data["strokes"])
        self.strokes_group.import_data(mesh, data["strokes"])

    def export_data(self):
        names = [stroke_edit.model.name for stroke_edit in self.strokes_group.all_strokes()]

        if any(name == "" for name in names) or len(names) != len(set(names)):
            responses.modal(self, False, "Invalid inputs", "Data contains empty or duplicate names.")
            return None, None

        strokes_data = dict([stroke_edit.model.data() for stroke_edit in self.strokes_group.all_strokes()])
        mesh = self.mesh.text()

        if not mesh or not strokes_data:
            responses.modal(self, False, "Error", "Nothing to Export, no data found.")
            return

        self.is_saved = True
        return mesh, strokes_data

    # • ———————————————————————————
    # • ———— Utils. ————

    def repaint(self):
        for stroke in self.strokes_group.all_strokes():
            stroke.set_colour()

    def cleanup(self):
        if not self.is_saved:
            if not responses.question(self, "Revert", "Are you sure you want to revert? All unsaved changes will be lost."):
                return

        default_text = self.mesh.property("default_text")
        self.mesh.setText(default_text)

        self.strokes_group.clear()
        self.regions.clear()

        self.is_saved = True
        api.remove_all_colours()
