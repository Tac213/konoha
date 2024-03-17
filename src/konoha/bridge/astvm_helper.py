# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PySide6 import QtCore, QtQml

from konoha.bridge import astvms
from konoha.bridge.astvms import astvm
from konoha import parser

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Python.ASTVMHelper"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QtQml.QmlElement
class ASTVMHelper(QtCore.QObject):

    @QtCore.Slot(result="QVariant")
    def get_astvm_category_info(self) -> dict:
        result = {}
        for astvm_class_name, astvm_class in astvms.ASTVM_MAP.items():
            astvm_categories = astvm_class.astvm_category.split(astvms.ASTVM_CATEGORY_SPLITTER)
            category_info = result
            for category in astvm_categories:
                category_info = category_info.setdefault(category, {})  # type: dict
            category_info[astvm_class_name] = True
        return result

    @QtCore.Slot(result=list)
    def get_all_astvm_class_names(self) -> list:
        return list(astvms.ASTVM_MAP.keys())

    @QtCore.Slot(str, result=str)
    def get_astvm_class_show_name(self, astvm_class_name: str) -> str:
        astvm_class = astvms.ASTVM_MAP.get(astvm_class_name)
        if not astvm_class:
            return "Unknown ASTVM"
        return astvm_class.astvm_name

    @QtCore.Slot(str, result=astvm.ASTVM)
    def create_astvm(self, astvm_class_name: str) -> astvm.ASTVM:
        astvm_class = astvms.ASTVM_MAP.get(astvm_class_name)
        assert astvm_class, f"No such astvm: {astvm_class_name}"
        ast_node = parser.create_ast(astvm_class.astvm_name)
        astvm_node = astvms.create_astvm(ast_node)
        return astvm_node
