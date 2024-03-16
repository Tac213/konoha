# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import os
import pathlib
from importlib import resources

from PySide6 import QtCore
from __feature__ import snake_case, true_property  # pylint: disable=import-error,unused-import

import konoha

ROOT_DIR = (
    getattr(sys, "_MEIPASS")  # PyInstaller
    if getattr(sys, "frozen", False)
    else (
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))  # Nuitka
        if hasattr(konoha, "__compiled__")
        else os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    )  # Source code
)
ROOT_PATH = (
    pathlib.Path(getattr(sys, "_MEIPASS"))  # PyInstaller
    if getattr(sys, "frozen", False)
    else (
        pathlib.Path(__file__).parent.parent.parent  # Nuitka
        if hasattr(konoha, "__compiled__")
        else pathlib.Path(__file__).parent.parent.parent.parent
    )  # Source code
)

DATA_PATH = resources.files("konoha").joinpath("data")
DATA_DIR = str(DATA_PATH)

LOCAL_APP_DATA_DIR = os.path.normpath(
    QtCore.QStandardPaths.standard_locations(QtCore.QStandardPaths.StandardLocation.AppLocalDataLocation)[0]
)  # pylint: disable=line-too-long
LOCAL_APP_DATA_PATH = pathlib.Path(LOCAL_APP_DATA_DIR)

LOG_DIR = os.path.join(ROOT_DIR, "log")
LOG_PATH = ROOT_PATH / "log"
