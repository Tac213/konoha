# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import os
import subprocess
import typing

from PySide6 import QtCore

from qt_quick_python_tools import deploy_utils
from qt_quick_python_tools import deploy_env


APP_ARGS = [
    f"--output-filename={deploy_utils.get_app_application_name()}",
    f"--product-name={deploy_utils.get_app_application_name()}",
    f"--product-version={deploy_utils.get_app_project_version()}",
]

QT_ARGS = [
    "--enable-plugin=pyside6",
    "--noinclude-qt-translations",
    "--include-qt-plugins=sensible,qml",
    "--noinclude-dlls=Qt6Concurrent*",
    "--noinclude-dlls=Qt6DataVisualization*",  # GPLv3
    "--noinclude-dlls=Qt6Labs*",
    "--noinclude-dlls=Qt6Multimedia*",
    "--noinclude-dlls=Qt6NetworkAuthorization*",  # GPLv3
    "--noinclude-dlls=Qt6Designer*",  # GPLv3
    "--noinclude-dlls=Qt6Widgets*",
    "--noinclude-dlls=Qt6OpenGLWidgets*",
    "--noinclude-dlls=Qt6Location*",
    # "--noinclude-dlls=Qt6Positioning*",
    "--noinclude-dlls=Qt6PrintSupport*",
    "--noinclude-dlls=Qt6Charts*",  # GPLv3
    "--noinclude-dlls=Qt63D*",
    "--noinclude-dlls=Qt6QMLXmlListModel*",
    "--noinclude-dlls=Qt6Quick3D*",  # GPLv3
    "--noinclude-dlls=Qt6QuickLocalStorage*",
    "--noinclude-dlls=Qt6QuickParticles*",
    "--noinclude-dlls=Qt6QuickTimeline*",  # GPLv3
    "--noinclude-dlls=Qt6QuickWidgets*",
    "--noinclude-dlls=Qt6QuickTest*",
    "--noinclude-dlls=Qt6RemoteObjects*",
    "--noinclude-dlls=Qt6SCXML*",
    "--noinclude-dlls=Qt6Sensors*",
    "--noinclude-dlls=Qt6SerialBus*",
    "--noinclude-dlls=Qt6SerialPort*",
    "--noinclude-dlls=Qt6ShaderTools*",  # GPLv3
    "--noinclude-dlls=Qt6StateMachine*",
    "--noinclude-dlls=Qt6SQL*",
    "--noinclude-dlls=Qt6Test*",
    "--noinclude-dlls=Qt6TextToSpeech*",
    "--noinclude-dlls=Qt6VirtualKeyboard*",  # GPLv3
    # "--noinclude-dlls=Qt6WebEngine*",
    # "--noinclude-dlls=Qt6WebChannel*",
    "--noinclude-dlls=Qt6WebSockets*",
    "--noinclude-dlls=Qt6XML*",
    "--noinclude-dlls=QtConcurrent*",
    "--noinclude-dlls=QtDataVisualization*",  # GPLv3
    "--noinclude-dlls=QtLabs*",
    "--noinclude-dlls=QtMultimedia*",
    "--noinclude-dlls=QtNetworkAuthorization*",  # GPLv3
    "--noinclude-dlls=QtDesigner*",  # GPLv3
    "--noinclude-dlls=QtWidgets*",
    "--noinclude-dlls=QtOpenGLWidgets*",
    "--noinclude-dlls=QtLocation*",
    # "--noinclude-dlls=QtPositioning*",
    "--noinclude-dlls=QtPrintSupport*",
    "--noinclude-dlls=QtCharts*",  # GPLv3
    "--noinclude-dlls=Qt3D*",
    "--noinclude-dlls=QtPdf*",
    "--noinclude-dlls=QtQmlXmlListModel*",
    "--noinclude-dlls=QtQuick3D*",  # GPLv3
    "--noinclude-dlls=QtQuickLocalStorage*",
    "--noinclude-dlls=QtQuickParticles*",
    "--noinclude-dlls=QtQuickTimeline*",  # GPLv3
    "--noinclude-dlls=QtQuickWidgets*",
    "--noinclude-dlls=QtQuickTest*",
    "--noinclude-dlls=QtRemoteObjects*",
    "--noinclude-dlls=QtScxml*",
    "--noinclude-dlls=QtSensors*",
    "--noinclude-dlls=QtSerialBus*",
    "--noinclude-dlls=QtSerialPort*",
    "--noinclude-dlls=QtShaderTools*",  # GPLv3
    "--noinclude-dlls=QtStateMachine*",
    "--noinclude-dlls=QtSql*",
    "--noinclude-dlls=QtTest*",
    "--noinclude-dlls=QtTextToSpeech*",
    "--noinclude-dlls=QtVirtualKeyboard*",  # GPLv3
    # "--noinclude-dlls=QtWebEngine*",
    # "--noinclude-dlls=QtWebChannel*",
    "--noinclude-dlls=QtWebSockets*",
    "--noinclude-dlls=QtXml*",
]

WIN32_ARGS = []

DARWIN_ARGS = [
    "--macos-create-app-bundle",
    f"--macos-app-name={deploy_utils.get_app_application_name()}",
    "--macos-app-mode=gui",
    f"--macos-signed-app-name=com.NetEaseGames.{deploy_utils.get_app_application_name()}",
]

LINUX_ARGS = []

DEBUG_ARGS = [
    "--debug",
    "--enable-console",
    "--force-stdout-spec=%PRODUCT%.out.txt",
    "--force-stderr-spec=%PRODUCT%.err.txt",
]

RELEASE_ARGS = [
    "--disable-console",
]


def get_script_args() -> typing.List[str]:
    return [
        deploy_env.entry_script,
        "--include-package=sunshine_boost",
        # assume that project name is same as root module name
        f"--include-package={deploy_env.app_root_module_name}",
    ]


def get_os_args() -> typing.List[str]:
    args = []
    icon_path = deploy_utils.get_app_application_icon()
    if sys.platform == "win32":
        args.extend(WIN32_ARGS)
        if icon_path.endswith(".ico"):
            args.append(f"--windows-icon-from-ico={icon_path}")
    if sys.platform == "darwin":
        args.extend(DARWIN_ARGS)
        if icon_path.endswith(".icns"):
            args.append(f"--macos-app-icon={icon_path}")
    if sys.platform == "linux":
        args.extend(LINUX_ARGS)
        if icon_path.endswith((".ico", ".png")):
            args.append(f"--linux-icon={icon_path}")
    return args


def get_variant_args() -> typing.List[str]:
    args = []
    if deploy_env.deployment_args.variant == "release":
        args.extend(RELEASE_ARGS)
    if deploy_env.deployment_args.variant == "debug":
        args.extend(DEBUG_ARGS)
    return args


def get_qtwebengine_args() -> typing.List[str]:
    qt_prefix_path = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.PrefixPath)
    qt_lib_path = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.LibrariesPath)
    if sys.platform == "win32":
        return [
            f"--include-data-files={qt_prefix_path}/QtWebEngineProcess.exe=QtWebEngineProcess.exe",
            f"--include-data-dir={qt_prefix_path}/translations/qtwebengine_locales=PySide6/translations/qtwebengine_locales",
            f"--include-data-dir={qt_prefix_path}/resources=PySide6/resources",
        ]
    if sys.platform == "darwin":
        return [
            f"--include-data-dir={qt_lib_path}/QtCore.framework=PySide6/Qt/lib/QtCore.framework",
            f"--include-data-dir={qt_lib_path}/QtDBus.framework=PySide6/Qt/lib/QtDBus.framework",
            f"--include-data-dir={qt_lib_path}/QtGui.framework=PySide6/Qt/lib/QtGui.framework",
            f"--include-data-dir={qt_lib_path}/QtNetwork.framework=PySide6/Qt/lib/QtNetwork.framework",
            f"--include-data-dir={qt_lib_path}/QtOpenGL.framework=PySide6/Qt/lib/QtOpenGL.framework",
            f"--include-data-dir={qt_lib_path}/QtPositioning.framework=PySide6/Qt/lib/QtPositioning.framework",
            f"--include-data-dir={qt_lib_path}/QtQml.framework=PySide6/Qt/lib/QtQml.framework",
            f"--include-data-dir={qt_lib_path}/QtQmlModels.framework=PySide6/Qt/lib/QtQmlModels.framework",
            f"--include-data-dir={qt_lib_path}/QtQuick.framework=PySide6/Qt/lib/QtQuick.framework",
            f"--include-data-dir={qt_lib_path}/QtWebChannel.framework=PySide6/Qt/lib/QtWebChannel.framework",
            f"--include-data-dir={qt_lib_path}/QtWebEngineCore.framework=PySide6/Qt/lib/QtWebEngineCore.framework",
        ]
    return []


def deploy_with_nuitka() -> int:
    output_directory = os.path.normpath(os.path.dirname(deploy_env.deployment_args.distpath))
    command_args = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        f"--output-dir={output_directory}",
        "--assume-yes-for-downloads",
    ]
    command_args.extend(get_script_args())
    command_args.extend(APP_ARGS)
    command_args.extend(QT_ARGS)
    command_args.extend(get_qtwebengine_args())
    command_args.extend(get_os_args())
    command_args.extend(get_variant_args())
    deploy_env.logger.info('Running command "%s" in "%s"', " ".join(command_args), deploy_env.root_path)
    stdout = deploy_utils.LogPipe(deploy_env.logger.info)
    stderr = deploy_utils.LogPipe(deploy_env.logger.error)
    with subprocess.Popen(
        command_args,
        stdout=stdout,
        stderr=stderr,
        cwd=deploy_env.root_path,
    ) as p:
        p.wait()
    stdout.close()
    stderr.close()
    return p.returncode
