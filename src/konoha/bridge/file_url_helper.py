# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PySide6 import QtCore, QtQml

from konoha.const import path_const

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Python.FileUrlHelper"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QtQml.QmlElement
class FileUrlHelper(QtCore.QObject):

    @QtCore.Property(str, constant=True)
    def root_dir(self) -> str:
        return QtCore.QUrl.from_local_file(path_const.ROOT_PATH).to_string()
