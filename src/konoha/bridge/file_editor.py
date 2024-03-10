# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PySide6 import QtCore, QtQml

from konoha import utils
from konoha.editor import file_editor
from konoha.bridge import astvms
from konoha.bridge.astvms import astvm

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Python.FileEditor"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QtQml.QmlElement
class FileEditor(QtCore.QObject):

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._file_editor = file_editor.FileEditor()

    @QtCore.Slot(str, result=astvm.mod_vm)
    def open_file(self, file_url: str) -> astvm.mod_vm:
        file_path = utils.parse_file_path_by_url(file_url)
        root_node = self._file_editor.open_file(file_path)
        tree_vm = astvms.create_astvm(root_node)
        return tree_vm

    @QtCore.Slot(str, astvm.mod_vm)
    def save_file(self, file_url: str, tree_vm: astvm.mod_vm) -> None:
        file_path = utils.parse_file_path_by_url(file_url)
        self._file_editor.save_file(file_path, tree_vm.model)
