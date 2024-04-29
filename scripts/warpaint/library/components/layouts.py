from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore


def to_group(layout, title=None):
    """Wraps a given layout in a group box.

    Args:
        layout (QLayout): The layout to be placed inside the group box.
        title (str, optional): The title of the group box."""

    group = QtWidgets.QGroupBox(title)
    group.setLayout(layout)
    return group


def to_scroll_area(layout, min_height=150, max_height=None):
    """Wraps a given layout in a scrollable area. This is useful for layouts that
    might contain more content than can be displayed in the available space.

    Args:
        layout (QLayout): The layout to be placed inside the scroll area.
        min_height (int, optional): The minimum height of the scroll area.
        max_height (int, optional): The maximum height of the scroll area.

    Returns:
        QtWidgets.QScrollArea: A scroll area containing the provided layout."""

    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    scroll_area.setWidgetResizable(True)

    scroll_area.setMinimumHeight(min_height)
    scroll_area.setMaximumHeight(max_height or 16777215)  # Max. 24-bit int.

    container = QtWidgets.QFrame(layout=layout, frameShape=QtWidgets.QFrame.NoFrame)
    layout.setAlignment(QtCore.Qt.AlignTop)

    scroll_area.setWidget(container)
    scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

    return scroll_area


def scroll_to_bottom(scroll_area):
    """Sets the scroll bar's value to its maximum, ensuring that the scroll area
    is scrolled all the way to the bottom.

    Parameters:
        scroll_area (QScrollArea): The scroll area widget to be scrolled to the
        bottom."""

    max_scroll_value = scroll_area.verticalScrollBar().maximum()
    scroll_area.verticalScrollBar().setValue(max_scroll_value)


def horizontal_divider(expand=False):
    """Creates a horizontal divider line. Useful for visually separating UI components.

    Args:
        expand (bool): If True, the divider will expand to fill the available space.

    Returns:
        QtWidgets.QFrame: A horizontal line frame widget."""

    frame = QtWidgets.QFrame()
    frame.setFrameShape(QtWidgets.QFrame.HLine)
    frame.setFrameShadow(QtWidgets.QFrame.Sunken)

    if expand:
        frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    return frame


def wrap_label(label, widget, horizontal=False):
    """Wraps a widget with a label in a vertical or horizontal layout.

    Args:
        label (str): Text for the label.
        widget (QtWidgets.QWidget): The widget to be wrapped.
        vertical (bool, optional): True for vertical, False for horizontal layout.

    Returns:
        QtWidgets.QLayout: Layout with the label and widget."""

    layout = QtWidgets.QHBoxLayout() if horizontal else QtWidgets.QVBoxLayout()
    layout.addWidget(QtWidgets.QLabel(label))
    layout.addWidget(widget)

    return layout


def header(text):
    """Creates a header label wrapped in a layout with the given text.

    Args:
        text (str): The text to be displayed in the label.

    Returns:
        QtWidgets.QLayout: A layout containing the title label."""

    font = QtGui.QFont()
    font.setCapitalization(QtGui.QFont.AllUppercase)
    font.setBold(True)

    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(horizontal_divider(True))
    layout.addWidget(QtWidgets.QLabel(text, font=font))
    layout.addWidget(horizontal_divider(True))

    return layout


def clear_radio_group(radio_group):
    """Clears the selection of a radio button group.

    Parameters:
        radio_group (QButtonGroup): The radio button group whose selection will be
    cleared."""

    exclusive_state = radio_group.exclusive()
    radio_group.setExclusive(False)

    for radio_button in radio_group.buttons():
        radio_button.setChecked(False)

    radio_group.setExclusive(exclusive_state)


def clear_layout(layout):
    """Recursively clears all items from a given layout. This includes deleting
    any widgets and clearing any nested layouts.

    Args:
        layout (QLayout): The layout to be cleared.

    Note:
        Widgets removed from the layout will be deleted. Nested layouts will be recursively
    cleared."""

    for index in reversed(range(layout.count())):
        child = layout.takeAt(index)

        widget = child.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        else:
            sub_layout = child.layout()
            if sub_layout is not None:
                clear_layout(sub_layout)


def invalidate_widget(widget, error):
    widget.setStyleSheet("border: 1px solid red;")
    widget.setToolTip(error)
    widget.setFocus()

    parent = widget.parent()

    while parent:
        if isinstance(parent, QtWidgets.QScrollArea):
            parent.ensureWidgetVisible(widget)

        parent = parent.parent()
