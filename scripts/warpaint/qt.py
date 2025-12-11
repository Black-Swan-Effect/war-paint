import importlib

binding = None

for module in ["PySide6", "PySide2"]:
    try:
        importlib.import_module(module)
        binding = module
        break
    except ImportError:
        ...


if binding == "PySide6":
    import shiboken6 as shiboken  # type: ignore

    from PySide6 import QtCore, QtGui, QtWidgets, QtSvg  # type: ignore
    from PySide6 import QtSvgWidgets, QtWebEngineWidgets, QtWebEngineCore  # type: ignore

    # QtGui.QAction -> PySide6 Syntax.
    # QtGui.QShortcut -> PySide6 Syntax.

    QSvgWidget = QtSvgWidgets.QSvgWidget
    QWebEngineView = QtWebEngineWidgets.QWebEngineView
    QWebEnginePage = QtWebEngineCore.QWebEnginePage


elif binding == "PySide2":
    import shiboken2 as shiboken  # type: ignore
    from PySide2 import QtCore, QtGui, QtWidgets, QtSvg  # type: ignore
    from PySide2 import QtWebEngineWidgets  # type: ignore

    QtGui.QAction = QtWidgets.QAction  # PySide2 -> PySide6 Syntax.
    QtGui.QShortcut = QtWidgets.QShortcut  # PySide2 -> PySide6 Syntax.

    QSvgWidget = QtSvg.QSvgWidget
    QWebEngineView = QtWebEngineWidgets.QWebEngineView
    QWebEnginePage = QtWebEngineWidgets.QWebEnginePage


class PySideRegex:
    """Compatibility layer for handling both QRegExp (PySide2) and QRegularExpression (PySide6)"""

    def __init__(self, pattern):
        if binding == "PySide6":
            self.regex = QtCore.QRegularExpression(pattern)
        else:  # PySide2
            self.regex = QtCore.QRegExp(pattern)

    def search(self, text, offset=0):
        if binding == "PySide6":
            match = self.regex.match(text, offset)
            if match.hasMatch():
                return match.capturedStart(), match.capturedLength()

            return -1, 0

        else:  # PySide2
            pos = self.regex.indexIn(text, offset)
            return pos, self.regex.matchedLength() if pos != -1 else 0


__all__ = [
    "shiboken",
    "QtWidgets",
    "QtCore",
    "QtGui",
    "QtSvg",
    "QAction",
    "QShortcut",
    "QSvgWidget",
    "QWebEngineView",
    "QWebEnginePage",
    "PySideRegex",
]
