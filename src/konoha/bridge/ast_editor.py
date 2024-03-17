# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PySide6 import QtCore, QtQml

from konoha.bridge.astvms import astvm
from konoha.editor import ast_editor

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Python.ASTEditor"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QtQml.QmlElement
class ASTEditor(QtCore.QObject):

    @QtCore.Slot(astvm.ASTVM, astvm.ASTVM, result=bool)
    def is_child(self, test_node: astvm.ASTVM, parent_node: astvm.ASTVM) -> bool:
        return ast_editor.is_child(test_node.model, parent_node.model)

    @QtCore.Slot(astvm.ASTVM, astvm.ASTVM, astvm.ASTVM)
    def insert_statement(self, root_node: astvm.ASTVM, previous_node: astvm.ASTVM, new_node: astvm.ASTVM) -> None:
        ast_editor.StatementInserter(previous_node.model, new_node.model).visit(root_node.model)

    @QtCore.Slot(astvm.ASTVM, astvm.ASTVM, astvm.ASTVM)
    def top_insert_statement(self, root_node: astvm.ASTVM, previous_top: astvm.ASTVM, new_top: astvm.ASTVM) -> None:
        ast_editor.StatementTopInserter(previous_top.model, new_top.model).visit(root_node.model)
