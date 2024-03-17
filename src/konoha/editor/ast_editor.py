# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import ast

from konoha import genv


def is_child(test_node: ast.AST, parent_node: ast.AST) -> bool:
    """
    Test if the test_node is the child of parent_node
    """
    return test_node in ast.iter_child_nodes(parent_node)


class StatementInserter(ast.NodeVisitor):
    """
    Insert a statement into an AST
    """

    def __init__(self, previous_node: ast.AST, new_node: ast.AST) -> None:
        super().__init__()
        self._previous_node = previous_node
        self._new_node = new_node

    def generic_visit(self, node: ast.AST) -> ast.AST:
        for field, old_value in ast.iter_fields(node):
            if not isinstance(old_value, list):
                continue
            is_statement_list = False
            insert_index = 0
            for idx, value in enumerate(old_value):
                is_statement_list = isinstance(value, ast.stmt)
                if value is self._previous_node:
                    insert_index = idx + 1
                    break
            if is_statement_list and insert_index > 0:
                old_value.insert(insert_index, self._new_node)
                genv.logger.info("Insert '%s' to the field '%s' of '%s' at index: %s", self._new_node, field, node, insert_index)
                break
        return node


class StatementTopInserter(ast.NodeVisitor):
    """
    Insert a statement to the top of an AST's child
    """

    def __init__(self, previous_top: ast.AST, new_top: ast.AST) -> None:
        super().__init__()
        self._previous_top = previous_top
        self._new_top = new_top

    def generic_visit(self, node: ast.AST) -> ast.AST:
        for field, old_value in ast.iter_fields(node):
            if not isinstance(old_value, list):
                continue
            if len(old_value) == 0:
                continue
            if old_value[0] is self._previous_top:
                old_value.insert(0, self._new_top)
                genv.logger.info("Insert '%s' to the field '%s' of '%s' at index: 0", self._new_top, field, node)
                break
        return node
