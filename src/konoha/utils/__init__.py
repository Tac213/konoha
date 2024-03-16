# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import importlib
from urllib import parse

from konoha import genv
from konoha.bridge import astvms


def parse_file_path_by_url(file_url: str) -> str:
    """
    Parse file path by url
    Args:
        file_url: url of the file, e.g. file:///D:/YourFolder/YourFile
    Returns:
        str
    """
    parse_result = parse.urlparse(file_url)
    maybe_path = parse.unquote_plus(parse_result.path)
    return maybe_path[1:] if sys.platform == "win32" else maybe_path


def reload() -> None:
    """
    Reload all modules of current package
    """
    if getattr(sys, "frozen", False):
        return
    prefix, _, _ = __name__.partition(".")
    modules = sys.modules.copy()
    for module_name, module in modules.items():
        if not module_name.startswith(prefix):
            continue
        importlib.reload(module)
        genv.logger.debug("Reload '%s' successfully.", module_name)
    astvms.register_astvms(genv.QML_ENGINE)
