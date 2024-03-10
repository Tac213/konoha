# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import logging

from PySide6 import QtCore

from konoha import bridge
from konoha.log import mock_stdout


def handler(mode: QtCore.QtMsgType, context: QtCore.QMessageLogContext, message: str) -> None:
    # available fields of context: category, file, function, line
    formatted_message = QtCore.qFormatLogMessage(mode, context, message)
    if bridge.output_window_bridge_object:
        if mode in (QtCore.QtMsgType.QtDebugMsg, QtCore.QtMsgType.QtInfoMsg):
            bridge.output_window_bridge_object.show_normal_message.emit(formatted_message)
        elif mode == QtCore.QtMsgType.QtWarningMsg:
            bridge.output_window_bridge_object.show_warning_message.emit(formatted_message)
        elif mode in (QtCore.QtMsgType.QtCriticalMsg, QtCore.QtMsgType.QtFatalMsg):
            bridge.output_window_bridge_object.show_error_message.emit(formatted_message)
    if mode in (QtCore.QtMsgType.QtDebugMsg, QtCore.QtMsgType.QtInfoMsg):
        if sys.__stdout__:
            sys.__stdout__.write(f"{formatted_message}\n")
        if isinstance(sys.stdout, mock_stdout.MockStdout):
            for file_handler in sys.stdout.file_handlers:
                file_handler.emit(logging.LogRecord("qt", logging.INFO, "", 0, formatted_message, (), None))
    else:
        if sys.__stderr__:
            sys.__stderr__.write(f"{formatted_message}\n")
        if isinstance(sys.stderr, mock_stdout.MockStdout):
            for file_handler in sys.stderr.file_handlers:
                file_handler.emit(logging.LogRecord("qt", logging.ERROR, "", 0, formatted_message, (), None))
