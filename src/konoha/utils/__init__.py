# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
from urllib import parse


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
