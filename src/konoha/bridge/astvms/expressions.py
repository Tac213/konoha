# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import ast
import typing

from PySide6 import QtCore

from konoha.utils import advanced_qt_property
from konoha.bridge import astvms
from konoha.bridge.astvms import astvm


@astvms.ast_node()
class comprehension_vm(astvm.ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.comprehension

    One `for` clause in a comprehension. `target` is the reference to use for each element - typically a Name or
    Tuple node. `iter` is the object to iterate over. `ifs` is a list of test expressions: each `for` clause can have
    multiple `ifs`.

    `is_async` indicates a comprehension is asynchronous (using an `async for` instead of `for`). The value is
    an integer (0 or 1).
    """

    target = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: astvm.expr_vm
    iter = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: astvm.expr_vm
    ifs = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[astvm.expr_vm]
    is_async = advanced_qt_property.AdvancedQtProperty(int)  # type: int

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._target = None
        self._iter = None
        self._ifs = []
        self._is_async = 0

    def initialize(self, model: ast.comprehension) -> None:
        super().initialize(model)
        self._target = astvms.create_astvm(model.target)
        self._iter = astvms.create_astvm(model.iter)
        for entry in model.ifs:
            self._ifs.append(astvms.create_astvm(entry))
        self._is_async = model.is_async


@astvms.ast_node()
class arg_vm(astvm.ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.arg

    A single argument in a list. `arg` is a raw string of the argument name; `annotation` is its annotation, such as
    a Name node.
    `type_comment` is an optional string with the type annotation as a comment
    """

    arg = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    annotation = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: str

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._arg = ""
        self._annotation = None

    def initialize(self, model: ast.arg) -> None:
        super().initialize(model)
        self._arg = model.arg
        self._annotation = astvms.create_astvm(model.annotation)


@astvms.ast_node()
class arguments_vm(astvm.ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.arguments

    The arguments for a function.
    - `posonlyargs`, `args` and `kwonlyargs` are lists of arg nodes.
    - `vararg` and `kwarg` are single arg nodes, referring to the `*args, **kwargs` parameters.
    - `kw_defaults` is a list of default values for keyword-only arguments. If one is `None`, the corresponding
      argument is required.
    - `defaults` is a list of default values for arguments that can be passed positionally. If there are fewer
      defaults, they correspond to the last n arguments.
    """

    posonlyargs = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[arg_vm]
    args = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[arg_vm]
    vararg = advanced_qt_property.AdvancedQtProperty(arg_vm)  # type: typing.Optional[arg_vm]
    kwonlyargs = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[arg_vm]
    kw_defaults = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[typing.Optional[astvm.expr_vm]]
    kwarg = advanced_qt_property.AdvancedQtProperty(arg_vm)  # type: typing.Optional[arg_vm]
    defaults = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[astvm.expr_vm]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._posonlyargs = []
        self._args = []
        self._vararg = None
        self._kwonlyargs = []
        self._kw_defaults = []
        self._kwarg = None
        self._defaults = []

    def initialize(self, model: ast.arguments) -> None:
        super().initialize(model)
        for entry in model.posonlyargs:
            self._posonlyargs.append(astvms.create_astvm(entry))
        for entry in model.args:
            self._args.append(astvms.create_astvm(entry))
        if model.vararg is not None:
            self._vararg = astvms.create_astvm(model.vararg)
        for entry in model.kwonlyargs:
            self._kwonlyargs.append(astvms.create_astvm(entry))
        for kwd in model.kw_defaults:
            if kwd is None:
                self._kw_defaults.append(None)
            else:
                self._kw_defaults.append(astvms.create_astvm(kwd))
        if model.kwarg is not None:
            self._kwarg = astvms.create_astvm(model.kwarg)
        for entry in model.defaults:
            self._defaults.append(astvms.create_astvm(entry))


@astvms.ast_node()
class keyword_vm(astvm.ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.keyword

    A keyword argument to a function call or class definition. `arg` is a raw string of the parameter name, `value`
    is a node to pass in.
    """

    arg = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    value = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: astvm.expr_vm

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._arg = ""
        self._value = None

    def initialize(self, model: ast.keyword) -> None:
        super().initialize(model)
        self._arg = model.arg
        self._value = astvms.create_astvm(model.value)


@astvms.ast_node()
class withitem_vm(astvm.ASTVM):  # pylint: disable=invalid-name
    """
    View Model of ast.withitem

    A single context manager in a `with` block. `context_expr` is the context manager, often a Call node.
    `ptional_vars` is a Name, Tuple or List for the `as foo` part, or `None` if that isn't used.
    """

    context_expr = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: astvm.expr_vm
    optional_vars = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: typing.Optional[astvm.expr_vm]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._context_expr = None
        self._optional_vars = None

    def initialize(self, model: ast.withitem) -> None:
        super().initialize(model)
        self._context_expr = astvms.create_astvm(model.context_expr)
        if model.optional_vars is not None:
            self._optional_vars = astvms.create_astvm(model.optional_vars)


@astvms.ast_node()
class Load(astvm.expr_context_vm):  # pylint: disable=invalid-name
    """
    View Model of ast.Load

    Variable references can be used to load the value of a variable, to assign a new value to it, or to delete it.
    Variable references are given a context to distinguish these cases.
    """


@astvms.ast_node()
class Store(astvm.expr_context_vm):  # pylint: disable=invalid-name
    """
    View Model of ast.Store

    Variable references can be used to load the value of a variable, to assign a new value to it, or to delete it.
    Variable references are given a context to distinguish these cases.
    """


@astvms.ast_node()
class Del(astvm.expr_context_vm):  # pylint: disable=invalid-name
    """
    View Model of ast.Del

    Variable references can be used to load the value of a variable, to assign a new value to it, or to delete it.
    Variable references are given a context to distinguish these cases.
    """


@astvms.ast_node(astvm.expr_vm)
class Name(astvm.expr_vm):
    """
    View Model of ast.Name

    A variable name. `id` holds the name as a string, and `ctx` is one of the following types.
    """

    id = advanced_qt_property.AdvancedQtProperty(str)  # type: str
    ctx = advanced_qt_property.AdvancedQtProperty(astvm.expr_context_vm)  # type: astvm.expr_context_vm

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._id = ""
        self._ctx = None

    def initialize(self, model: ast.Name) -> None:
        super().initialize(model)
        self._id = model.id
        self._ctx = astvms.create_astvm(model.ctx)


@astvms.ast_node(astvm.expr_vm)
class Constant(astvm.expr_vm):
    """
    View Model of ast.Constant

    A constant value. The `value` attribute of the `Constant` literal contains the Python object it represents. The
    values represented can be simple types such as a number, string or `None`, but also immutable container
    types (tuples and frozensets) if all of their elements are constant.
    """

    value = advanced_qt_property.AdvancedQtProperty("QVariant")  # type: typing.Any
    kind = advanced_qt_property.AdvancedQtProperty(str)  # type: typing.Optional[str]
    s = advanced_qt_property.AdvancedQtProperty("QVariant")  # type: typing.Any
    n = advanced_qt_property.AdvancedQtProperty("QVariant")  # type: typing.Union[int, float, complex]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._value = None
        self._kind = ""
        self._s = None
        self._n = None

    def initialize(self, model: ast.Constant) -> None:
        super().initialize(model)
        self._value = model.value
        self._kind = model.kind
        self._s = model.s
        self._n = model.n


@astvms.ast_node(astvm.expr_vm)
class Call(astvm.expr_vm):
    """
    View Model of ast.expr

    A function call. `func` is the function, which will often be a Name or Attribute object. Of the arguments:
    - `args` holds a list of the arguments passed by position.
    - `keywords` holds a list of keyword objects representing arguments passed by keyword.
    hen creating a `Call` node, `args` and `keywords` are required, but they can be empty lists.
    """

    func = advanced_qt_property.AdvancedQtProperty(astvm.expr_vm)  # type: astvm.expr_vm
    args = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[astvm.expr_vm]
    keywords = advanced_qt_property.AdvancedQtProperty("QVariantList")  # type: list[keyword_vm]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._func = None
        self._args = []
        self._keywords = []

    def initialize(self, model: ast.Call) -> None:
        super().initialize(model)
        self._func = astvms.create_astvm(model.func)
        for entry in model.args:
            self._args.append(astvms.create_astvm(entry))
        for entry in model.keywords:
            self._keywords.append(astvms.create_astvm(entry))
