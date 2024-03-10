# -*- mode: python ; coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.datastruct import TOC
from PyInstaller.utils.hooks import qt

from qt_quick_python_tools import deploy_env
from qt_quick_python_tools import deploy_utils

block_cipher = None
qtwebengine_binaries, qtwebengine_data = qt.pyside6_library_info.collect_qtwebengine_files()

a = Analysis(
    deploy_env.scripts,
    pathex=deploy_env.pathex,
    binaries=qtwebengine_binaries,
    datas=qtwebengine_data,
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
    icon=deploy_utils.get_app_application_icon() if deploy_utils.get_app_application_icon().endswith((".ico", ".exe")) else None,
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
    "Qt6Concurrent",
    "Qt6DataVisualization",  # GPLv3
    "Qt6Labs",
    "Qt6Multimedia",
    "Qt6NetworkAuthorization",  # GPLv3
    "Qt6Designer",  # GPLv3
    "Qt6Widgets",
    "Qt6OpenGLWidgets",
    "Qt6Location",
    # "Qt6Positioning",
    "Qt6PrintSupport",
    "Qt6Charts",  # GPLv3
    "Qt63D",
    "Qt6Pdf",
    "Qt6QMLXmlListModel",
    "Qt6Quick3D",  # GPLv3
    "Qt6QuickLocalStorage",
    "Qt6QuickParticles",
    "Qt6QuickTimeline",  # GPLv3
    "Qt6QuickWidgets",
    "Qt6QuickTest",
    "Qt6RemoteObjects",
    "Qt6SCXML",
    "Qt6Sensors",
    "Qt6SerialBus",
    "Qt6SerialPort",
    "Qt6ShaderTools",  # GPLv3
    "Qt6StateMachine",
    "Qt6SQL",
    "Qt6Test",
    "Qt6TextToSpeech",
    "Qt6VirtualKeyboard",  # GPLv3
    # "Qt6WebEngine",
    # "Qt6WebChannel",
    "Qt6WebSockets",
    "Qt6XML",
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
    upx=True,
    upx_exclude=[],
    name=deploy_utils.get_app_application_name(),
)
