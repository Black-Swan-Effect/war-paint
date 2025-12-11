from maya import OpenMayaUI
from warpaint.qt import QtWidgets, QtCore, shiboken

from warpaint import ROOT_DIR


def maya_window():
    """Retrieves the main Maya window in order to parent the UI to it.

    Returns:
        QtWidgets.QWidget: The main Maya window."""

    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class Singleton(type(QtCore.QObject)):
    """A metaclass that creates a Singleton instance for QtCore.QObjects."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]


class BaseTemplate(QtWidgets.QDialog, metaclass=Singleton):
    """Base class for all main UIs that feature single instance, proper StyleSheet
    and Icon search paths. The UI is also parented to the main Maya window."""

    raise_window = QtCore.Signal()
    close_window = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, parent=maya_window())
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool & ~QtCore.Qt.WindowContextHelpButtonHint)

        icons_dir = ROOT_DIR.joinpath("resources/icons")
        if icons_dir.as_posix() not in QtCore.QDir.searchPaths(icons_dir.name):
            QtCore.QDir.setSearchPaths(icons_dir.name, [icons_dir.as_posix()])

        css_filepath = ROOT_DIR.joinpath("resources/css/style.css")
        self.setStyleSheet(css_filepath.read_text())

    # • ———————————————————————————
    # • ———— Utils. ————

    @classmethod
    def launch(cls):
        """Launches a new or the existing instance of the class and shows or
        raises the window."""

        instance = cls()

        if instance.isHidden():
            instance.show()

        instance.raise_()
        instance.activateWindow()

        return instance

    @classmethod
    def del_instances(cls):
        """Deletes all instances of the class."""

        for instance in cls._instances.values():
            instance.close()
            instance.setParent(None)
            instance.deleteLater()

        cls._instances.clear()

    # • ———————————————————————————
    # • ———— Events. ————

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_window.emit()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.close_window.emit()
