# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import argparse

from PySide6 import QtCore, QtGui, QtQml
from PySide6 import QtQuick  # pylint: disable=unused-import
from __feature__ import snake_case, true_property  # pylint: disable=import-error,unused-import

from konoha import bridge
from konoha import genv
from konoha.const import app_const
from konoha.log import qt_message_handler
from konoha.utils import enhanced_qml_application_engine
from konoha import resource_view_rc  # pylint: disable=import-error,unused-import


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    return parser


def main(args) -> int:
    """
    entry function
    Args:
        args: Argument parsed by get_argument_parser()
    Returns:
        int, returncode of current process
    """
    QtCore.qInstallMessageHandler(qt_message_handler.handler)
    QtGui.QGuiApplication.set_attribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QtGui.QGuiApplication.set_attribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QtGui.QGuiApplication()
    app.application_name = app_const.APP_NAME
    app.application_display_name = app_const.APP_NAME
    app.desktop_file_name = app_const.APP_NAME
    app.organization_name = app_const.ORGANIZATION_NAME
    app.window_icon = QtGui.QIcon(app_const.APP_ICON)

    bridge.register_bridges()
    bridge.initialize_bridge_objects()
    engine = enhanced_qml_application_engine.EnhancedQmlApplicationEngine("view/MainWindow.qml")
    genv.initialize(engine)
    bridge_objects = bridge.get_bridge_objects()
    property_pair = QtQml.QQmlContext.PropertyPair()
    property_pair.name = "qmlEngine"
    property_pair.value = engine
    bridge_objects.append(property_pair)
    engine.root_context().set_context_properties(bridge_objects)
    engine.load_entry_qml()
    if not engine.root_objects():
        return -1

    returncode = app.exec()
    bridge.finalize_bridge_objects()
    genv.finalize()

    return returncode
