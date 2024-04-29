from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore


class ComboboxModal(QtWidgets.QComboBox):
    item_renamed = QtCore.Signal(str, str)
    item_deleted = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    # • ───────────────────────────
    # • ──── Context Menu. ────

    def context_menu(self, position):
        menu = QtWidgets.QMenu()
        menu.addAction(QtGui.QIcon("icons:add.svg"), "Add", self.add_item)
        menu.addAction(QtGui.QIcon("icons:edit.svg"), "Edit", self.edit_item)
        menu.addAction(QtGui.QIcon("icons:delete.svg"), "Delete", self.delete_item)

        menu.exec_(self.mapToGlobal(position))

    def add_item(self):
        text, valid = QtWidgets.QInputDialog.getText(self, "New Item", "Enter Name:")

        if valid and text:
            self.addItem(text)
            self.setCurrentIndex(self.count() - 1)

    def edit_item(self):
        if self.currentIndex() == 0:
            return  # Cannot edit "all" section.

        current_text = self.currentText()
        new_text, valid = QtWidgets.QInputDialog.getText(self, "Edit Item", "Enter Name:", text=self.currentText())

        if valid and (new_text not in [self.itemText(index) for index in range(self.count())]):
            self.setItemText(self.currentIndex(), new_text)
            self.item_renamed.emit(current_text, new_text)

    def delete_item(self):
        if self.currentIndex() == 0:
            return  # Cannot delete "all" section.

        message = "Are you sure you want to delete the item '{}'?".format(self.currentText())
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(self, "Delete Item", message):
            current_text = self.currentText()
            self.removeItem(self.currentIndex())
            self.item_deleted.emit(current_text)

    # • ───────────────────────────
    # • ──── Utils. ────

    def all_items(self):
        return [self.itemText(index) for index in range(self.count())]
