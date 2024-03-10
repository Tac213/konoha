# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import os
import subprocess
import typing
from importlib import resources

from qt_quick_python_tools import deploy_env
from qt_quick_python_tools import deploy_utils
from qt_quick_python_tools import shader_baker

QRC_FILE_NAME = "resource_view.qrc"
PY_RC_FILE_NAME = "resource_view_rc.py"
QT_QUICK_CONTROLS_CONF_FILE_NAME = "qtquickcontrols2.conf"
EXCLUDE_DIR_NAMES = (
    ".git",
    ".svn",
    "__pycache__",
)
EXCLUDE_EXTS = (
    ".py",
    ".pyc",
    ".qrc",
    ".qml~",
)

qt_quick_controls_conf_file_relpath = ""


def _add_all_resources(resource_dir: str, prefix: str) -> typing.List[str]:
    global qt_quick_controls_conf_file_relpath

    content = [f'<qresource prefix="{prefix}">']
    for root, _, file_names in os.walk(resource_dir):
        if os.path.basename(root) in EXCLUDE_DIR_NAMES:
            continue
        for file_name in file_names:
            if file_name.endswith(EXCLUDE_EXTS):
                continue
            file_path = os.path.join(root, file_name)
            file_relpath = os.path.relpath(file_path, deploy_env.root_path).replace(os.path.sep, "/")
            if file_name == QT_QUICK_CONTROLS_CONF_FILE_NAME:
                qt_quick_controls_conf_file_relpath = file_relpath
                continue
            alias = os.path.relpath(file_path, resource_dir).replace(os.path.sep, "/")
            content.append(f'    <file alias="{alias}">{file_relpath}</file>')
    content.append("</qresource>")
    return content


def _add_all_views(view_dir: str, prefix: str) -> typing.List[str]:
    global qt_quick_controls_conf_file_relpath

    content = [f'<qresource prefix="{prefix}">']
    for root, _, file_names in os.walk(view_dir):
        if os.path.basename(root) in EXCLUDE_DIR_NAMES:
            continue
        for file_name in file_names:
            if file_name.endswith(EXCLUDE_EXTS):
                continue
            file_path = os.path.join(root, file_name)
            file_relpath = os.path.relpath(file_path, deploy_env.root_path).replace(os.path.sep, "/")
            if file_name == QT_QUICK_CONTROLS_CONF_FILE_NAME:
                qt_quick_controls_conf_file_relpath = file_relpath
                continue
            alias = os.path.relpath(file_path, view_dir).replace(os.path.sep, "/")
            content.append(f'    <file alias="{alias}">{file_relpath}</file>')
    content.append("</qresource>")
    return content


def _add_all_shaders(shader_dir: str, prefix: str) -> typing.List[str]:
    content = [f'<qresource prefix="{prefix}">']
    for root, _, file_names in os.walk(shader_dir):
        if os.path.basename(root) in EXCLUDE_DIR_NAMES:
            continue
        for file_name in file_names:
            if not file_name.endswith(shader_baker.QSB_EXT):
                continue
            file_path = os.path.join(root, file_name)
            file_relpath = os.path.relpath(file_path, deploy_env.root_path).replace(os.path.sep, "/")
            alias = os.path.relpath(file_path, shader_dir).replace(os.path.sep, "/")
            content.append(f'    <file alias="{alias}">{file_relpath}</file>')
    content.append("</qresource>")
    return content


def generate_qrc_file() -> int:
    content = ['<!DOCTYPE RCC><RCC version="1.0">']

    config = deploy_utils.get_qt_quick_python_tools_config() or {}
    if deploy_env.app_root_module_name is not None:
        # assume that project name is same as root module name
        # and all resource files is placed in data folder under root module folder
        qrc_config = config.get("qrc-config", {})
        resource_dirname = qrc_config.get("resource-directory-name", "resource")
        view_dirname = qrc_config.get("view-directory-name", "view")
        shader_dirname = qrc_config.get("shader-directory-name", "shader")
        project_data_dir = str(resources.files(deploy_env.app_root_module_name).joinpath("data"))
        project_resource_dir = os.path.join(project_data_dir, resource_dirname)
        project_view_dir = os.path.join(project_data_dir, view_dirname)
        project_shader_dir = os.path.join(project_data_dir, shader_dirname)
        if os.path.exists(project_resource_dir):
            content.extend(_add_all_resources(project_resource_dir, f"{deploy_env.app_root_module_name}/{resource_dirname}"))
        if os.path.exists(project_view_dir):
            content.extend(_add_all_views(project_view_dir, f"{deploy_env.app_root_module_name}/{view_dirname}"))
        if os.path.exists(project_shader_dir):
            deploy_env.logger.info("Found shader directory, try to bake shaders.")
            returncode = shader_baker.main(project_shader_dir)
            if returncode:
                deploy_env.logger.error("Failed to bake shader. See logs above.")
                return returncode
            content.extend(_add_all_shaders(project_shader_dir, f"{deploy_env.app_root_module_name}/{shader_dirname}"))

    if qt_quick_controls_conf_file_relpath:
        content.append('<qresource prefix="/">')
        content.append(f'    <file alias="{QT_QUICK_CONTROLS_CONF_FILE_NAME}">{qt_quick_controls_conf_file_relpath}</file>')
        content.append("</qresource>")

    content.append("</RCC>")

    qrc_file_path = os.path.join(deploy_env.root_path, QRC_FILE_NAME)
    with open(qrc_file_path, "w+", encoding="utf-8") as fp:
        fp.write("\n".join(content))

    return 0


def compile_qrc_file() -> int:
    pyside6_rcc_executable = os.path.join(os.path.dirname(sys.executable), "pyside6-rcc")
    command = f"{pyside6_rcc_executable} {QRC_FILE_NAME} > src/{deploy_env.app_root_module_name}/{PY_RC_FILE_NAME}"
    deploy_env.logger.info('Running command "%s" in "%s"', command, deploy_env.root_path)
    stdout = deploy_utils.LogPipe(deploy_env.logger.info)
    stderr = deploy_utils.LogPipe(deploy_env.logger.error)
    with subprocess.Popen(
        command,
        stdout=stdout,
        stderr=stderr,
        shell=True,
        cwd=deploy_env.root_path,
    ) as p:
        p.wait()
        stdout.close()
        stderr.close()
    return p.returncode


def main() -> int:
    deploy_env.logger.info("Generating %s", QRC_FILE_NAME)
    returncode = generate_qrc_file()
    if returncode:
        return returncode
    deploy_env.logger.info("Generating %s", PY_RC_FILE_NAME)
    return compile_qrc_file()


if __name__ == "__main__":
    sys.exit(main())
