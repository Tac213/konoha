# -*- coding: utf-8 -*-
# author: Tac
# contact: cookiezhx@163.com

import sys
import os
import argparse
import shutil
from importlib import resources

import PyInstaller.__main__

from qt_quick_python_tools import resource_compiler
from qt_quick_python_tools import deploy_env


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", "-t", type=str, choices=["pyinstaller", "nuitka"], default="pyinstaller")
    parser.add_argument("--variant", "-v", type=str, choices=["debug", "release"], default="release")
    parser.add_argument("--distpath", "-d", type=str, default=os.path.join(os.getcwd(), "deployment", "dist"))
    parser.add_argument("--workpath", "-b", type=str, default=os.path.join(os.getcwd(), "deployment", "build"))
    return parser


def main(args):
    if not os.path.isfile("pyproject.toml"):
        deploy_env.logger.error("Deployment should be performed in your project's root path.")
        sys.exit(-1)
    deploy_env.logger.info("Start deployment.")
    deploy_env.logger.info("tool: %s", args.tool)
    deploy_env.logger.info("variant: %s", args.variant)
    deploy_env.logger.info("distpath: %s", args.distpath)
    deploy_env.logger.info("workpath: %s", args.workpath)
    returncode = resource_compiler.main()
    if returncode:
        deploy_env.logger.error("Failed to compile resource. See logs above.")
        sys.exit(returncode)
    if os.path.exists(args.workpath):
        deploy_env.logger.info("Workpath '%s' exists, pending to remove it.", args.workpath)
        shutil.rmtree(args.workpath)
    if args.tool == "pyinstaller":
        PyInstaller.__main__.run(
            [
                os.path.join(str(resources.files("qt_quick_python_tools").joinpath("")), "spec", f"{sys.platform}.spec"),
                "--distpath",
                args.distpath,
                "--workpath",
                args.workpath,
                "--noconfirm",
            ]
        )
    else:
        from qt_quick_python_tools.spec import nuitka_spec  # pylint: disable=import-outside-toplevel

        sys.exit(nuitka_spec.deploy_with_nuitka())


if __name__ == "__main__":
    deploy_env.parse_deployment_args()
    main(deploy_env.deployment_args)
