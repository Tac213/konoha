# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import ast
import importlib
import typing

from PySide6 import QtCore, QtQml
from __feature__ import snake_case, true_property  # pylint: disable=import-error,unused-import

from konoha.bridge.astvms import astvm

ALL_ASTVM_MODULES = (
    "expressions",
    "statements",
    "root_nodes",
)
ASTVM_MAP: dict[str, astvm.ASTVM] = {}
ASTVM_COMPONENT_MAP: dict[str, QtQml.QQmlComponent] = {}


class ASTVMIncubator(QtQml.QQmlIncubator):
    """
    ASTVM Component Incubator
    """

    def __init__(
        self,
        tree: ast.AST,
        on_created: typing.Callable[[astvm.ASTVM], None],
        mode: QtQml.QQmlIncubator.IncubationMode = QtQml.QQmlIncubator.IncubationMode.Asynchronous,
    ) -> None:
        super().__init__(mode)
        self._tree = tree
        self._on_created = on_created

    def status_changed(self, status: QtQml.QQmlIncubator.Status) -> None:
        super().status_changed(status)
        if status == QtQml.QQmlIncubator.Status.Ready:
            vm = self.object()
            assert isinstance(vm, astvm.ASTVM)
            vm.initialize(self._tree)
            self._on_created(vm)
        elif status == QtQml.QQmlIncubator.Status.Error:
            assert False, "\n".join(error.to_string() for error in self.errors())


def ast_node(parent_class: type[astvm.ASTVM] = astvm.ASTVM) -> type[astvm.ASTVM]:
    """
    Decorate a astvm class to register it
    """

    def real_decorator(astvm_class: type[astvm.ASTVM]):
        assert issubclass(astvm_class, parent_class), f"'{astvm_class.__name__}' is not a subclass of '{parent_class.__name__}'."
        QtQml.qmlRegisterType(astvm_class, "Python.ASTVM", 1, 0, _get_qml_type_name(astvm_class.__name__))
        assert astvm_class.__name__ not in ASTVM_MAP, f"Duplicated ASTVM: '{astvm_class.__name__}'"
        ASTVM_MAP[astvm_class.__name__] = astvm_class
        return astvm_class

    return real_decorator


def register_astvms(engine: QtQml.QQmlApplicationEngine) -> None:
    """
    register all nodes
    Returns:
        None
    """
    for module_name in ALL_ASTVM_MODULES:
        importlib.import_module(f".{module_name}", __name__)
    for astvm_name in ASTVM_MAP:
        # Create a component factory and load the QML script
        component = QtQml.QQmlComponent(engine)
        component.load_from_module("Python.ASTVM", _get_qml_type_name(astvm_name))
        ASTVM_COMPONENT_MAP[astvm_name] = component


def create_astvm(tree: ast.AST) -> astvm.ASTVM:
    astvm_class_name = tree.__class__.__name__
    astvm_component = ASTVM_COMPONENT_MAP.get(astvm_class_name)
    assert astvm_component is not None, f"No such astvm: '{astvm_class_name}'"
    vm = astvm_component.create()
    assert vm is not None, "\n".join(error.to_string() for error in astvm_component.errors())
    assert isinstance(vm, astvm.ASTVM)
    vm.initialize(tree)
    return vm


def create_astvm_async(tree: ast.AST, on_created: typing.Callable[[astvm.ASTVM], None]) -> None:
    astvm_class_name = tree.__class__.__name__
    astvm_component = ASTVM_COMPONENT_MAP.get(astvm_class_name)
    assert astvm_component is not None, f"No such astvm: '{astvm_class_name}'"
    # Create an incubator to instantiate asynchronously
    incubator = ASTVMIncubator(tree, on_created)
    astvm_component.create(incubator)


def _get_qml_type_name(type_name: str) -> str:
    assert len(type_name) > 0, "QML element type name should not be empty string."
    if type_name[0].upper() == type_name[0]:
        return type_name
    return f"{type_name[0].upper()}{type_name[1:]}"
