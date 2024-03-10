# -*- mode: python ; coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT

from qt_quick_python_tools import deploy_env
from qt_quick_python_tools import deploy_utils

block_cipher = None

a = Analysis(
    deploy_env.scripts,
    pathex=deploy_env.pathex,
    binaries=[],
    datas=[],
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
    icon=deploy_utils.get_app_application_icon() if deploy_utils.get_app_application_icon().endswith((".ico")) else None,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=deploy_utils.get_app_application_name(),
)
