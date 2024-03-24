#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2 import QtWidgets  # type: ignore


INFORMATION_COLOUR = "#0ea5e9"
ERROR_COLOUR = "#f87171"


class MessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIcon(QtWidgets.QMessageBox.NoIcon)


def modal(parent, success, message, details=None):
    colour = INFORMATION_COLOUR if success else ERROR_COLOUR

    formatted_text = "<p align='center' style='font-weight: bold; color:{colour}'>{message}</p>"
    formatted_text += "<p align='center'>{details}</p>" if details else ""

    message_box = MessageBox(parent)
    message_box.setWindowTitle("Success" if success else "Error")
    message_box.setText(formatted_text.format(message=message, colour=colour, details=details))
    message_box.show()


def question(parent, message, details=None):
    formatted_text = "<p align='center' style='font-weight: bold; color:{colour}'>{message}</p>"
    formatted_text += "<p align='center'>{details}</p>" if details else ""

    message_box = MessageBox(parent)
    message_box.setWindowTitle("Question")
    message_box.setText(formatted_text.format(message=message, colour=INFORMATION_COLOUR, details=details))
    message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

    return QtWidgets.QMessageBox.Yes == message_box.exec()
