# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
from PySide6 import QtCore, QtQml

from konoha import genv
from konoha.const import path_const


class EnhancedQmlApplicationEngine(QtQml.QQmlApplicationEngine):
    def __init__(self, entry_qml_suffix, parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self._entry_qml = self.get_file_url(entry_qml_suffix)

    def load_entry_qml(self) -> None:
        self.load(self._entry_qml)

    @QtCore.Slot()
    def reload(self) -> None:
        if self.is_release:  # pylint: disable=using-constant-test
            return
        self.clear_component_cache()
        genv.logger.debug("Reloading: '%s'", self._entry_qml)
        self.load(self._entry_qml)

    @QtCore.Slot(str, result=str)
    def get_file_url(self, suffix) -> str:
        """
        Get file from qrc in release mode
        Get file from file url in development mode
        So that all qml files can be reloaded in development mode, including resources
        """
        if self.is_release:  # pylint: disable=using-constant-test
            return f"qrc:/konoha/{suffix}"
        file_path = path_const.DATA_PATH / suffix
        return QtCore.QUrl.from_local_file(file_path).to_string()

    @QtCore.Property(bool, constant=True)
    def is_release(self) -> bool:
        return getattr(sys, "frozen", False)
