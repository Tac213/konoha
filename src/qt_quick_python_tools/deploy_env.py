# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import os
import logging
from importlib import resources

from qt_quick_python_tools import deploy
from qt_quick_python_tools import deploy_utils

logger = logging.getLogger("deployment")

deployment_args = None

root_path = os.getcwd()
app_root_module_name = deploy_utils.get_app_root_module_name()
project_source_path = str(resources.files(app_root_module_name).joinpath(""))
deployment_path = str(resources.files("qt_quick_python_tools").joinpath(""))

all_source_modules = list(deploy_utils.iterate_all_modules(project_source_path))

entry_script = os.path.join(project_source_path, "__main__.py")
scripts = [entry_script]
pathex = []
hiddenimports = [f"{app_root_module_name}.resource_view_rc"]
hiddenimports.extend(all_source_modules)


def parse_deployment_args():
    global deployment_args
    deployment_args = deploy.get_argument_parser().parse_args(sys.argv[1:])
