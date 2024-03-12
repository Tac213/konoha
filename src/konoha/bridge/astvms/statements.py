# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import ast
import typing

from PySide6 import QtCore

from konoha.utils import advanced_qt_property
from konoha.parser import ast_extension
from konoha.bridge import astvms
from konoha.bridge.astvms import astvm


@astvms.ast_node()
class alias_vm(astvm.ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.alias

    Both parameters are raw strings of the names. `asname` can be `None` if the regular name is to be used.
    """

    name = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    asname = advanced_qt_property.AdvancedQtProperty(str)  # type: typing.Optional[str]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._name = ""
        self._asname = ""

    def initialize(self, model: ast.alias) -> None:
        super().initialize(model)
        self._name = model.name
        self._asname = model.asname


@astvms.ast_node(astvm.stmt_vm)
class Expr(astvm.stmt_vm):
    """
    View Model of ast.Expr

    When an expression, such as a function call, appears as a statement by itself with its return value not used
    or stored, it is wrapped in this container. `value` holds one of the other nodes in this section, a Constant, a
    Name, a Lambda, a Yield or YieldFrom node.
    """

    value = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: astvm.expr_vm

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._value = None

    def initialize(self, model: ast.Expr) -> None:
        super().initialize(model)
        self._value = astvms.create_astvm(model.value)
        self._node_description = "{{ value }}"
        self._argument_property_names = ["value"]


@astvms.ast_node(astvm.stmt_vm)
class Comment(astvm.stmt_vm):
    """
    View Model of ast_extension.Comment
    """

    value = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    inline = advanced_qt_property.AdvancedQtProperty(bool)  # type: bool

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._value = ""
        self._inline = False

    def initialize(self, model: ast_extension.Comment) -> None:
        super().initialize(model)
        self._value = model.value
        self._inline = model.inline


if sys.version_info >= (3, 10):

    @astvms.ast_node()
    class pattern_vm(astvm.ASTVM):  # pylint: disable=invalid-name
        """
        View Model of ast.pattern
        """

    @astvms.ast_node()
    class match_case_vm(astvm.ASTVM):  # pylint: disable=invalid-name
        """
        View Model of ast.match_case
        """

        pattern = advanced_qt_property.AdvancedQtProperty(pattern_vm)  # type: pattern_vm
        guard = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: typing.Optional[astvm.expr_vm]
        body = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[astvm.stmt_vm]

        def __init__(self, parent: QtCore.QObject | None = None) -> None:
            super().__init__(parent)
            self._pattern = None
            self._guard = None
            self._body = []

        def initialize(self, model: ast.match_case) -> None:
            super().initialize(model)
            self._pattern = astvms.create_astvm(model.pattern)
            if model.guard:
                self._guard = astvms.create_astvm(model.guard)
            for entry in model.body:
                self._body.append(astvms.create_astvm(entry))
