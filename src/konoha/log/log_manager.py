# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import logging
import enum
import typing
import time
import os

from konoha.log import logger as logger_module
from konoha.log import output_window_handler
from konoha.log import mock_stdout


@enum.unique
class LogLevel(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogManager(object):
    created_logger_names = set()
    level = LogLevel.DEBUG

    @classmethod
    def get_logger(
        cls, logger_name: str, log_to_output_window: bool = True, save_file: bool = True, dirname: typing.Optional[str] = None
    ) -> logger_module.Logger:
        if logger_name in cls.created_logger_names:
            return logging.getLogger(logger_name)

        logger = logging.getLogger(logger_name)
        logger.setLevel(cls.level.value)
        if save_file and dirname:
            logger.addHandler(cls._create_handler(logger_name, save_file, dirname))
        if log_to_output_window:
            logger.addHandler(cls._create_handler(logger_name))
        cls.created_logger_names.add(logger_name)

        return logger

    @classmethod
    def _create_handler(cls, logger_name: str, save_file=False, dirname=None):
        con = " - "
        # comment of logging.Formatter lists all available keys
        format_list = ["%(asctime)s", "%(name)s", "%(levelname)s", "%(message)s"]
        if save_file and dirname:
            filename = os.path.join(dirname, f'{logger_name}_{time.strftime("%Y%m%d_%H%M%S")}.log')
            handler = logging.FileHandler(filename, encoding="utf-8")
            if isinstance(sys.stdout, mock_stdout.MockStdout):
                sys.stdout.add_file_handler(handler)
            if isinstance(sys.stderr, mock_stdout.MockStdout):
                sys.stderr.add_file_handler(handler)
        else:
            # handler = logging.StreamHandler(sys.stdout)
            handler = output_window_handler.OutputWindowHandler()

        handler.setLevel(cls.level.value)
        formatter = logging.Formatter(con.join(format_list))
        handler.setFormatter(formatter)
        return handler

    @classmethod
    def set_level(cls, level: LogLevel):
        cls.level = level
        for logger_name in cls.created_logger_names:
            logger = logging.getLogger(logger_name)
            logger.setLevel(level.value)
            for handler in logger.handlers:
                handler.setLevel(level.value)

    @classmethod
    def setup_std_logger(cls) -> None:
        if not isinstance(sys.stdout, mock_stdout.MockStdout):
            sys.stdout = mock_stdout.MockStdout(mock_stdout.ChannelType.STDOUT, sys.__stdout__)
        if not isinstance(sys.stderr, mock_stdout.MockStdout):
            sys.stderr = mock_stdout.MockStdout(mock_stdout.ChannelType.STDERR, sys.__stderr__)
