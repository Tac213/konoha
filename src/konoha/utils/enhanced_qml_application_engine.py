# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
from PySide6 import QtCore, QtQml


class EnhancedQmlApplicationEngine(QtQml.QQmlApplicationEngine):
    def __init__(self, entry_qml: str, parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self._entry_qml = entry_qml

    def load_entry_qml(self) -> None:
        self.load(self._entry_qml)

    @QtCore.Slot()
    def reload(self) -> None:
        if self.is_release:  # pylint: disable=using-constant-test
            return
        self.clear_component_cache()
        self.load(self._entry_qml)

    @QtCore.Property(bool, constant=True)
    def is_release(self) -> bool:
        return getattr(sys, "frozen", False)
