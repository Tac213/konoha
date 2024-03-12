# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import ast

from PySide6 import QtCore

from konoha.utils import advanced_qt_property


class ASTVM(QtCore.QObject, metaclass=advanced_qt_property.QObjectMeta):  # pylint: disable=invalid-metaclass
    """
    View Model of ast.AST
    """

    lineno = advanced_qt_property.AdvancedQtProperty(int)  # type: int
    col_offset = advanced_qt_property.AdvancedQtProperty(int)  # type: int
    end_lineno = advanced_qt_property.AdvancedQtProperty(int)  # type: int
    end_col_offset = advanced_qt_property.AdvancedQtProperty(int)  # type: int
    type_comment = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    # Editor specific
    is_statement = advanced_qt_property.AdvancedQtProperty(bool)  # type: bool
    is_code_block = advanced_qt_property.AdvancedQtProperty(bool)  # type: bool
    node_description = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    node_block_descriptions = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[str]
    argument_property_names = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[str]
    input_argument_type_map = advanced_qt_property.AdvancedQtProperty("QVariant")  # type: dict[str, str]
    code_block_map = advanced_qt_property.AdvancedQtProperty("QVariant")  # type: dict[str, int]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.model = None
        self._lineno = 0
        self._col_offset = 0
        self._end_lineno = 0
        self._end_col_offset = 0
        self._type_comment = ""
        # Editor specific
        self._is_statement = False
        self._is_code_block = False
        self._node_description = ""
        self._node_block_descriptions = []
        self._argument_property_names = []
        self._input_argument_type_map = {}
        self._code_block_map = []

    def initialize(self, model: ast.AST) -> None:
        self.model = model
        if hasattr(model, "lineno"):
            self._lineno = model.lineno
        if hasattr(model, "col_offset"):
            self._col_offset = model.col_offset
        if hasattr(model, "end_lineno"):
            self._end_lineno = model.end_lineno
        if hasattr(model, "end_col_offset"):
            self._end_col_offset = model.end_col_offset
        if hasattr(model, "type_comment"):
            self._type_comment = model.type_comment


class mod_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.mod
    """


class type_ignore_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.type_ignore
    """


class stmt_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.stmt
    """

    def initialize(self, model: ast.stmt) -> None:
        super().initialize(model)
        self._is_statement = True


class expr_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.expr
    """


class expr_context_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.expr_context
    """


class boolop_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.boolop
    """


class operator_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.operator
    """


class unaryop_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.unaryop
    """


class cmpop_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.cmpop
    """


class excepthandler_vm(ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.excepthandler
    """


if sys.version_info >= (3, 12):

    class type_param_vm(ASTVM):  # pylint: disable=invalid-name
        """
        View Model of ast.type_param
        """
