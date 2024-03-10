# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import ast
from konoha.utils import singleton
from konoha.parser import parser


class FileEditor(object, metaclass=singleton.MetaSingleton):

    @classmethod
    def open_file(cls, file_path: str) -> ast.AST:
        return parser.parse_by_file_path(file_path)

    @classmethod
    def save_file(cls, file_path: str, tree: ast.AST) -> None:
        parser.unparse_to_file_path(tree, file_path)
