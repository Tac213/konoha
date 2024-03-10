# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import os
import threading
from importlib import machinery, resources
import toml
from toml import decoder

_project_toml = None
if os.path.isfile("pyproject.toml"):
    try:
        _project_toml = toml.load("pyproject.toml")
    except decoder.TomlDecodeError:
        pass


def iterate_all_modules(source_dir):
    validate_suffixes = tuple(machinery.SOURCE_SUFFIXES + machinery.EXTENSION_SUFFIXES)
    for root, _, file_names in os.walk(source_dir):
        for file_name in file_names:
            if not file_name.endswith(validate_suffixes):
                continue
            file_path = os.path.join(root, file_name)
            module_name = os.path.splitext(os.path.relpath(file_path, os.path.dirname(source_dir)))[0].replace(os.path.sep, ".")
            if module_name.endswith("__init__"):
                module_name = module_name.rpartition(".")[0]
            yield module_name


def get_app_root_module_name():
    project_name = get_app_project_name()
    config = get_qt_quick_python_tools_config() or {}
    return config.get("root-module-name", project_name)


def get_app_project_name():
    project_info = _project_toml.get("project")
    if project_info is None:
        return None
    return project_info.get("name")


def get_app_project_version():
    project_info = _project_toml.get("project")
    if project_info is None:
        return None
    return project_info.get("version", "unknown")


def get_qt_quick_python_tools_config():
    tool_config = _project_toml.get("tool")
    if not tool_config:
        return None
    return tool_config.get("qt-quick-python-tools")


def get_app_project_data_directory():
    root_module_name = get_app_root_module_name()
    if root_module_name is None:
        return None
    return str(resources.files(root_module_name).joinpath("data"))


def get_app_project_resource_directory():
    data_dir = get_app_project_data_directory()
    if data_dir is None:
        return None
    config = get_qt_quick_python_tools_config() or {}
    qrc_config = config.get("qrc-config", {})
    resource_dirname = qrc_config.get("resource-directory-name", "resource")
    return os.path.join(data_dir, resource_dirname)


def get_app_project_view_directory():
    data_dir = get_app_project_data_directory()
    if data_dir is None:
        return None
    config = get_qt_quick_python_tools_config() or {}
    qrc_config = config.get("qrc-config", {})
    view_dirname = qrc_config.get("view-directory-name", "view")
    return os.path.join(data_dir, view_dirname)


def get_app_project_shader_directory():
    data_dir = get_app_project_data_directory()
    if data_dir is None:
        return None
    config = get_qt_quick_python_tools_config() or {}
    qrc_config = config.get("qrc-config", {})
    shader_dirname = qrc_config.get("shader-directory-name", "shader")
    return os.path.join(data_dir, shader_dirname)


def get_app_application_name():
    default = "Unknown"
    config = get_qt_quick_python_tools_config() or {}
    deployment_config = config.get("deployment-config", {})
    return deployment_config.get("application-name", default)


def get_app_application_icon():
    default = ""
    data_dir = get_app_project_data_directory()
    if data_dir is None:
        return default
    config = get_qt_quick_python_tools_config() or {}
    deployment_config = config.get("deployment-config", {})
    icon_path = deployment_config.get(f"application-icon-{sys.platform}", default)
    return os.path.join(data_dir, icon_path)


class LogPipe(threading.Thread):
    def __init__(self, log_function) -> None:
        super().__init__()
        self.daemon = False
        self.fd_read, self.fd_write = os.pipe()
        self.pipe_reader = os.fdopen(self.fd_read)
        self._log_function = log_function
        self.start()

    def fileno(self) -> int:
        """
        Return the write file descriptor of the pipe
        """
        return self.fd_write

    def run(self):
        """
        Run the thread, logging everything.
        """
        for line in iter(self.pipe_reader.readline, ""):
            self._log_function(line.strip("\n"))
        self.pipe_reader.close()

    def close(self):
        """
        Close the write end of the pipe.
        """
        os.close(self.fd_write)
