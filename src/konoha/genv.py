# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import os

from PySide6 import QtQml

from konoha.const import path_const, app_const
from konoha.log import logger as logger_module
from konoha.log import log_manager
from konoha.bridge import astvms

logger = None  # type: logger_module.Logger


def initialize(engine: QtQml.QQmlApplicationEngine) -> None:
    _init_logger()
    astvms.register_astvms(engine)


def _init_logger() -> None:
    global logger
    if not os.path.isdir(path_const.LOG_DIR):
        os.mkdir(path_const.LOG_DIR)
    log_manager.LogManager.setup_std_logger()
    logger = log_manager.LogManager.get_logger(app_const.APP_NAME, save_file=True, dirname=path_const.LOG_DIR)


def finalize() -> None:
    pass
