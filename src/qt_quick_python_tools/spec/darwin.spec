# -*- mode: python ; coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.datastruct import TOC
from PyInstaller.building.osx import BUNDLE
from PyInstaller.utils.hooks import qt

from qt_quick_python_tools import deploy_env
from qt_quick_python_tools import deploy_utils

block_cipher = None

qtwebengine_datas = []
for data in qt.pyside6_library_info.collect_qtwebengine_files()[1]:
    if data[1] == ".":
        continue
    qtwebengine_datas.append(data)

a = Analysis(
    deploy_env.scripts,
    pathex=deploy_env.pathex,
    binaries=[],
    datas=qtwebengine_datas,
    hiddenimports=deploy_env.hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=deploy_utils.get_app_application_name(),
    icon=deploy_utils.get_app_application_icon() if deploy_utils.get_app_application_icon().endswith(".icns") else None,
    debug=deploy_env.deployment_args.variant == "debug",
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=deploy_env.deployment_args.variant == "debug",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

excludes = (
    "QtConcurrent",
    "QtDataVisualization",  # GPLv3
    "QtLabs",
    "QtMultimedia",
    "QtNetworkAuthorization",  # GPLv3
    "QtDesigner",  # GPLv3
    "QtWidgets",
    "QtOpenGLWidgets",
    "QtLocation",
    # "QtPositioning",
    "QtPrintSupport",
    "QtCharts",  # GPLv3
    "Qt3D",
    "QtPdf",
    "QtQmlXmlListModel",
    "QtQuick3D",  # GPLv3
    "QtQuickLocalStorage",
    "QtQuickParticles",
    "QtQuickTimeline",  # GPLv3
    "QtQuickWidgets",
    "QtQuickTest",
    "QtRemoteObjects",
    "QtScxml",
    "QtSensors",
    "QtSerialBus",
    "QtSerialPort",
    "QtShaderTools",  # GPLv3
    "QtStateMachine",
    "QtSql",
    "QtTest",
    "QtTextToSpeech",
    "QtVirtualKeyboard",  # GPLv3
    # "QtWebEngine",
    # "QtWebChannel",
    "QtWebSockets",
    "QtXml",
)

binaries = []

for binary in a.binaries:
    is_need_exclude = False
    for exclude_str in excludes:
        if exclude_str in binary[0]:
            is_need_exclude = True
    if is_need_exclude:
        continue
    binaries.append(binary)

coll = COLLECT(
    exe,
    TOC(binaries),
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=deploy_utils.get_app_application_name(),
)

app = BUNDLE(
    coll,
    name=f"{deploy_utils.get_app_application_name()}.app",
    version=deploy_utils.get_app_project_version(),
    icon=deploy_utils.get_app_application_icon() if deploy_utils.get_app_application_icon().endswith(".icns") else None,
    bundle_identifier="org.qt-project.Qt.QtWebEngineCore",
    info_plist={
        "NSPrincipalClass": "NSApplication",
        "NSAppleScriptEnabled": True,
    },
)
