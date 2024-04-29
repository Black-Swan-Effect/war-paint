from maya import cmds
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore
import json, collections
from functools import partial

from warpaint.library import api
from warpaint.library.components import responses
from warpaint.library.utils import hashing, explorer, clipboard


EXTENSIONS = [".paint", ".tff"]
FILE_EXTENSION = ".paint"


class FilterProxyModel(QtCore.QSortFilterProxyModel):
    def filterAcceptsRow(self, row, parent):
        index = self.sourceModel().index(row, 0, parent)
        file_info = self.sourceModel().fileInfo(index)

        if file_info.isDir():
            return True

        if file_info.isFile():
            return any(file_info.fileName().endswith(ext) for ext in EXTENSIONS)


class FileSystemTree(QtWidgets.QTreeView):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings

        collections.deque(map(lambda index: self.hideColumn(index), range(1, self.model().columnCount())), 0)
        self.header().hide()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def get_path(self):
        proxy = self.model()  # FilterProxyModel
        model = proxy.sourceModel()  # QFileSystemModel

        current_index = self.currentIndex()
        proxy_index = proxy.mapToSource(current_index)
        return Path(model.filePath(proxy_index) or self.settings["root_dir"])

    def set_path(self, path):
        proxy = self.model()  # FilterProxyModel
        model = proxy.sourceModel()  # QFileSystemModel

        root_index = model.setRootPath(path.as_posix())
        proxy_index = proxy.mapFromSource(root_index)
        self.setRootIndex(proxy_index)

        return path

    # • ———————————————————————————
    # • ———— Context Menu. ————

    def context_menu(self, position):
        menu = QtWidgets.QMenu()
        current_path = self.get_path()

        if current_path:
            menu.addAction(QtGui.QIcon("icons:folder_open.svg"), "Show in Folder", partial(self.open_folder, current_path))
            menu.addAction(QtGui.QIcon("icons:copy.svg"), "Copy Path", partial(self.copy_path, current_path))
            menu.exec_(self.viewport().mapToGlobal(position))

    def open_folder(self, path):
        explorer.open_path(path.parent if path.is_file() else path)

    def copy_path(self, path):
        clipboard.clipboard_copy(path.as_posix())


class FilesUI(QtWidgets.QWidget):
    def __init__(self, settings, loading, paint, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.loading = loading
        self.paint = paint

        self.setup_widgets()
        self.setup_layouts()
        self.bind_connections()

    # • ───────────────────────────
    # • ──── UI. ────

    def setup_widgets(self):
        self.directory_preview = QtWidgets.QLineEdit("", placeholderText="Select Root Directory", readOnly=True)
        self.set_directory_button = QtWidgets.QPushButton(icon=QtGui.QIcon("icons:folder_open.svg"))

        self.file_system_model = QtWidgets.QFileSystemModel(filter=(QtCore.QDir.Files | QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot))
        self.file_system_proxy = FilterProxyModel(self, sourceModel=self.file_system_model)
        self.file_system_tree = FileSystemTree(self.settings, model=self.file_system_proxy, sortingEnabled=True)

        self.export_filename = QtWidgets.QLineEdit(placeholderText="Filename")
        self.export_button = QtWidgets.QPushButton("Export", icon=QtGui.QIcon("icons:folder_open.svg"))

    def setup_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        directory_layout = QtWidgets.QHBoxLayout()
        directory_layout.addWidget(self.directory_preview)
        directory_layout.addWidget(self.set_directory_button)
        main_layout.addLayout(directory_layout)

        self.file_system_layout = QtWidgets.QVBoxLayout()
        self.file_system_layout.addWidget(self.file_system_tree)
        main_layout.addLayout(self.file_system_layout)

        self.export_layout = QtWidgets.QHBoxLayout()
        self.export_layout.addWidget(self.export_filename)
        self.export_layout.addWidget(self.export_button)
        main_layout.addLayout(self.export_layout)

    # • ———————————————————————————
    # • ———— Populate. ————

    def populate(self):
        root_dir_str = self.settings["root_dir"]
        root_dir = Path(root_dir_str) if root_dir_str else None
        root_dir = root_dir if (root_dir and root_dir.exists()) else Path.home()

        path = self.file_system_tree.set_path(root_dir)
        self.directory_preview.setText(path.as_posix())
        self.settings["root_dir"] = path.as_posix()

    # • ———————————————————————————
    # • ———— Connections. ————

    def bind_connections(self):
        self.set_directory_button.clicked.connect(self.on_select_directory)
        self.file_system_tree.clicked.connect(self.on_populate_filename)
        self.file_system_tree.doubleClicked.connect(self.on_import)
        self.export_button.clicked.connect(self.on_export)

    def on_select_directory(self):
        current_directory_str = self.directory_preview.text()
        directory_str = QtWidgets.QFileDialog.getExistingDirectory(None, "Choose a project directory", current_directory_str)

        if directory_str:
            self.settings["root_dir"] = directory_str
            self.directory_preview.setText(directory_str)
            self.file_system_tree.set_path(Path(directory_str))

    def on_populate_filename(self):
        current_path = self.file_system_tree.get_path()

        if current_path:
            filename = current_path.stem if current_path.is_file() else ""
            self.export_filename.setText(filename)

    def on_import(self):
        current_path = self.file_system_tree.get_path()

        if not current_path or not current_path.is_file():
            return

        if current_path.suffix != FILE_EXTENSION:
            responses.modal(self, False, "Please select a .paint file.")
            return

        with self.loading():
            selection = cmds.filterExpand(selectionMask=12)
            selection = selection[0] if selection else None

            if not selection:
                responses.modal(self, False, "Please select a mesh.")
                return

            data = json.loads(current_path.read_text())
            data_hash = data.get("point_order_hash", None)

            point_order = list(api.get_point_order(selection))
            selection_hash = hashing.hash_str(str(point_order))

            if selection_hash != data_hash:
                if not responses.question(self, "Warning", "The meshes do not match (different point order). Apply anyway?"):
                    return

            self.paint.import_data(selection, data)
            tab = self.parentWidget().parentWidget()
            tab.setCurrentIndex(tab.indexOf(self.paint))

    def on_export(self):
        with self.loading():
            filename = self.export_filename.text()
            current_path = self.file_system_tree.get_path()

            if not filename:
                responses.modal(self, False, "Warning", "Please enter a filename.")
                return

            if not current_path:
                responses.modal(self, False, "Warning", "Please select a directory.")
                return

            target_directory = current_path if current_path.is_dir() else current_path.parent
            filepath = target_directory.joinpath(f"{filename}{FILE_EXTENSION}")

            if filepath.exists():
                if not responses.question(self, "Warning", f"File '{filepath.stem}' already exists. Overwrite?"):
                    return

            mesh, strokes_data = self.paint.export_data()

            if mesh and strokes_data:
                point_order = list(api.get_point_order(mesh))
                selection_hash = hashing.hash_str(str(point_order))
                filepath.write_text(json.dumps({"point_order_hash": selection_hash, "strokes": strokes_data}, indent=4))

                responses.modal(self, True, "Success", f"Exported to: {filepath}")
                return
