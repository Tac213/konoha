# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import ast

from konoha.parser import ast_extension


def create_ast(ast_class_name: str, /, **kwargs) -> ast.AST:
    ast_class = getattr(ast, ast_class_name, None)
    if ast_class is None:
        ast_class = getattr(ast_extension, ast_class_name, None)
    assert ast_class is not None, f"No such ast: {ast_class_name}"
    assert issubclass(ast_class, ast.AST), f"'{ast_class_name}' is not a subclass of ast.AST"
    fields = ast_class._fields
    for field in fields:
        if field in kwargs:
            continue
        kwargs[field] = None
    return ast_class(**kwargs)
