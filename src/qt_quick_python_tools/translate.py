"""
 # @ Author: haozeyu@corp.netease.com
 # @ Create Time: 2024-01-03 19:54:08
 # @ Description: Generate .ts file and .qm file.
 """

import os
import subprocess
from importlib import resources
from qt_quick_python_tools import deploy_utils
from qt_quick_python_tools import deploy_env

EXCLUDE_DIR_NAMES = (
    ".git",
    ".svn",
    "__pycache__",
)
EXCLUDE_EXTS = (
    ".pyc",
    ".qrc",
    ".qml~",
    ".ts",
    ".png",
    ".frag",
    ".icns",
    ".ico",
    ".ttf",
    ".qm",
    ".wav",
    ".svg",
    ".otf",
    ".qsb",
    ".mov",
    ".conf",
)


def main():
    lupdate = str(resources.files("PySide6").joinpath("lupdate"))
    lrelease = str(resources.files("PySide6").joinpath("lrelease"))
    project_name = deploy_utils.get_app_project_name()
    app_dir = str(resources.files(f"{project_name}").joinpath(""))
    translation_dir = str(resources.files(f"{project_name}").joinpath("data/translations"))
    files = []
    for root, _, filenames in os.walk(app_dir):
        if os.path.basename(root) in EXCLUDE_DIR_NAMES:
            continue
        for filename in filenames:
            if filename == "resource_view_rc.py":
                continue
            if filename.endswith(EXCLUDE_EXTS):
                continue
            files.append((os.path.relpath(os.path.join(root, filename), deploy_env.root_path).replace("\\", "/")))
    with open("translate_file", "w", encoding="utf-8") as f:
        for line in files:
            f.write(line)
            f.write("\n")
    # gengerate ts file
    with subprocess.Popen([lupdate, "@translate_file", "-no-obsolete", "-ts", os.path.join(translation_dir, "en_US.ts")]) as _:
        pass
    os.remove("translate_file")

    # compile qm file
    with subprocess.Popen([lrelease, os.path.join(translation_dir, "en_US.ts"), os.path.join(translation_dir, "en_US.qm")]) as _:
        pass


if __name__ == "__main__":
    main()
