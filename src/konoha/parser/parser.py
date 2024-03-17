# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import io
import ast

import black

from konoha import genv
from konoha.parser import ast_extension


def parse_by_file_path(file_path: str) -> ast.AST:
    """
    Parse ast by file path
    """
    with io.open_code(file_path) as fp:
        tree = ast_extension.parse(fp.read(), filename=file_path)
    genv.logger.info("Load AST of file '%s':\n%s", file_path, ast.dump(tree, indent=4))
    return tree


def unparse_to_file_path(tree: ast.AST, file_path) -> None:
    with io.open(file_path, "w", encoding="utf-8") as fp:
        content = ast_extension.unparse(tree)
        content = black.format_str(content, mode=black.Mode())
        fp.write(content)
    genv.logger.info("Save AST to file '%s':\n%s", file_path, ast.dump(tree, indent=4))
