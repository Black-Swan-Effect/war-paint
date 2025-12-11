#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from warpaint.qt import QtCore, QtGui


log = logging.getLogger(__name__)


def open_path(path):
    """Opens a file or directory using the default program on the user's system.
    if the path is a directory, it will open the directory in the default file
    explorer.

    Args:
    - path (Path): file or directory to be opened."""

    if path:
        file_url = f"file:{path.as_posix()}"
        if not QtGui.QDesktopServices.openUrl(QtCore.QUrl(file_url, QtCore.QUrl.TolerantMode)):
            log.error(f"Failed to open file in explorer: {file_url}")
