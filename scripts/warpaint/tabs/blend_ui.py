#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from maya import cmds
from PySide2 import QtGui, QtCore, QtWidgets  # type: ignore

from warpaint.library import api
from warpaint.library.components import layouts
from warpaint.library.utils import blendshapes


FOLLICLE_NAME, BLENDSHAPE, ALIAS = "warPaintFollicle", "warPaint", "ShapeShift"
CAMERA_NAME, GROUP_NAME = "warPaintCamera", "warPaintGroup"
CAMERA_OFFSET = 42


class BlenderUI(QtWidgets.QWidget):
    colours_changed = QtCore.Signal()

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings

        self.setup_widgets()
        self.setup_layout()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.base_mesh = QtWidgets.QLineEdit(placeholderText="base Mesh", readOnly=True)
        self.base_mesh.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.add_base_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:add.svg"), toolTip="Add Base Mesh")

        self.morph_mesh = QtWidgets.QLineEdit(placeholderText="Compare Mesh", readOnly=True)
        self.morph_mesh.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.add_morph_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:add.svg"), toolTip="Add Morph Mesh")

        self.blend_button = QtWidgets.QPushButton("Create BlendShape")
        self.blend_button.setProperty("default_text", "Create BlendShape")

        self.blend_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.unblend_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:delete.svg"), toolTip="Remove BlendShape")
        self.unblend_button.setProperty("state", "error_hover")

        self.blend_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, minimum=0, maximum=100)

        self.track_button = QtWidgets.QPushButton("Track Polygon")
        self.track_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.untrack_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:delete.svg"), toolTip="Untrack Polygon")
        self.untrack_button.setProperty("state", "error_hover")

    def setup_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        grid_layout = QtWidgets.QGridLayout(spacing=6)
        grid_layout.addWidget(QtWidgets.QLabel("Base Mesh:"), 0, 0)
        grid_layout.addWidget(self.base_mesh, 0, 1)
        grid_layout.addWidget(self.add_base_button, 0, 2)

        grid_layout.addWidget(QtWidgets.QLabel("Morph Mesh:"), 1, 0)
        grid_layout.addWidget(self.morph_mesh, 1, 1)
        grid_layout.addWidget(self.add_morph_button, 1, 2)

        grid_layout.addWidget(self.blend_button, 2, 0, 1, 2)
        grid_layout.addWidget(self.unblend_button, 2, 2)

        main_layout.addWidget(layouts.to_group(grid_layout, "BlendShape Setup"))
        main_layout.addStretch()

        slider_layout = QtWidgets.QHBoxLayout(spacing=6)
        slider_layout.addWidget(self.blend_slider)
        main_layout.addWidget(layouts.to_group(slider_layout, "Adjust BlendShape"))

        track_layout = QtWidgets.QHBoxLayout(spacing=6)
        track_layout.addWidget(self.track_button)
        track_layout.addWidget(self.untrack_button)
        main_layout.addWidget(layouts.to_group(track_layout, "Track Polygon"))

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.add_base_button.clicked.connect(self.add_base)
        self.add_morph_button.clicked.connect(self.add_morph)
        self.blend_button.clicked.connect(self.on_blend_setup)
        self.unblend_button.clicked.connect(self.remove_blendshape)

        self.blend_slider.valueChanged.connect(self.on_blend_change)

        self.track_button.clicked.connect(self.track_polygon)
        self.untrack_button.clicked.connect(self.untrack_polygon)

    def add_base(self):
        selection = cmds.filterExpand(cmds.ls(selection=True), selectionMask=12)
        self.base_mesh.setText(selection[0] if selection else "")

    def add_morph(self):
        selection = cmds.filterExpand(cmds.ls(selection=True), selectionMask=12)
        self.morph_mesh.setText(selection[0] if selection else "")

    def on_blend_change(self, value):
        blendshape = f"{BLENDSHAPE}.{ALIAS}"

        if cmds.objExists(blendshape):
            cmds.setAttr(blendshape, value / 100.0)

    def on_blend_setup(self):
        base_mesh = self.base_mesh.text()
        morph_mesh = self.morph_mesh.text()

        if not base_mesh or not cmds.objExists(base_mesh):
            return

        if not morph_mesh or not cmds.objExists(morph_mesh):
            return

        if base_mesh == morph_mesh:
            return

        blendshapes.delete_blendshape(morph_mesh, blendshape=BLENDSHAPE)
        blendshapes.create_blendshape(base_mesh, morph_mesh, name=BLENDSHAPE, alias=ALIAS)

        self.blend_button.setText("Blendshape created!")
        default_text = self.blend_button.property("default_text")
        QtCore.QTimer.singleShot(2000, lambda: self.blend_button.setText(default_text))

    def remove_blendshape(self):
        morph_mesh = self.morph_mesh.text()
        blendshapes.delete_blendshape(morph_mesh, blendshape=BLENDSHAPE)

        self.base_mesh.clear()
        self.morph_mesh.clear()

    def track_polygon(self):
        self.untrack_polygon()

        selection = cmds.filterExpand(selectionMask=34)
        selection = selection[0] if selection else None

        if not selection:
            return

        # -- Create Follicle.
        follicle = blendshapes.create_centered_follicle(face=selection, name=FOLLICLE_NAME)
        follicle_position = cmds.xform(follicle, query=True, translation=True)

        # -- Create Camera.
        camera = cmds.camera(name=CAMERA_NAME)[0]
        camera_group = cmds.group(camera, name=GROUP_NAME)

        # -- Define Camera Position.
        face_normal = api.get_face_normal(selection)
        camera_position = [v + o for v, o in zip(follicle_position, face_normal * CAMERA_OFFSET)]
        cmds.xform(camera, translation=camera_position)

        # -- Constraint.
        cmds.pointConstraint(follicle, camera_group, maintainOffset=True)
        cmds.delete(cmds.aimConstraint(follicle, camera, aimVector=[0, 0, -1]))

        cmds.lookThru(camera)

    def untrack_polygon(self):
        for name in [FOLLICLE_NAME, CAMERA_NAME, GROUP_NAME]:
            if cmds.objExists(name):
                cmds.delete(name)

        cmds.lookThru("persp")
