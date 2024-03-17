"""
Script for assembling application
"""

import sys
import os
import re
import types
import dataclasses
import site
import shutil
import itertools
import importlib
from importlib import machinery, util


from PyInstaller import hooks
from PyInstaller.building import build_main
from PyInstaller.utils import misc
from PyInstaller.utils.hooks import qt

from qt_quick_python_tools import generate_frozen_modules


@dataclasses.dataclass
class AssembleInfo:
    """
    Data struct for assemble info
    """

    entry_module_name: str  # A python module name or a signle python_file
    qml_directory: str
    hidden_imports: list[str]  # hidden import module names
    excludes: list[str]  # exclude module names
    binaries: list[str]  # list all needed binaries
    datas: list[str]  # list all needed datas
    pyside6_modules: list[str]  # list all used PySide6 module
    qt_quick_control_styles: list[str]  # list all needed QtQuick.Control stypes
    output_directory = os.path.join(generate_frozen_modules.ROOT_DIR, "deployment")
    ignore_platform_dynload = True
    static_python = True


@dataclasses.dataclass
class QtQmlModuleInfo:
    """
    Data struct for Qt Qml modules
    """

    name: str
    module_path: str
    qmldir_path: str
    import_modules: list[str]

    def __hash__(self):
        return hash((self.name, self.module_path, self.qmldir_path))

    def __eq__(self, other: "QtQmlModuleInfo") -> bool:
        return self.name == other.name


class PyiPySide6HookModule(types.ModuleType):
    """
    Type helper class for PyInstaller PySide6 hook modules
    """

    hiddenimports: list[str]
    binaries: list[tuple[str, str]]
    datas: list[tuple[str, str]]


def get_platform_dynload_dir() -> str:
    """
    Get platform dynamic load directory
    Returns:
        str
    """
    for path in sys.path:
        if path.endswith(("DLLs", "lib-dynload")):
            return path
    raise FileNotFoundError


def is_qtquick_application(assemble_info: AssembleInfo) -> bool:
    """
    Returns whether the application is a QtQuick application
    """
    return "PySide6.QtQuick" in assemble_info.pyside6_modules


def import_pyi_pyside6_hooks(fullname: str) -> PyiPySide6HookModule:
    """
    import PyInstaller PySide6 hook modules
    Args:
        name: fullname of PySide6 module
    Returns:
        PyiPySide6HookModule
    """
    hooks_dir = os.path.dirname(hooks.__file__)
    module_path = os.path.join(hooks_dir, f"hook-{fullname}.py")
    real_fullname = f"PyInstaller.hooks.{fullname}"
    loader = machinery.SourceFileLoader(real_fullname, module_path)
    spec = util.spec_from_file_location(real_fullname, module_path, loader=loader)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_used_qml_module_names(dir_path: str) -> list[str]:
    """
    Get qml module names that are used in a directory
    Args:
        dir_path (str): path of the directory
    Returns:
        list: module names
    """
    imports = []
    for root, _, file_names in os.walk(dir_path):
        for file_name in file_names:
            if file_name.endswith(".qml"):
                file_path = os.path.join(root, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # match: import <ModuleIdentifier> [<Version.Number>] [as <Qualifier>]
                pattern = re.compile(r"^import\s+([a-zA-Z][a-zA-Z0-9_\.]*)\s*", re.M)
                file_imports = pattern.findall(content)
                temp_list = [item for item in file_imports if item not in imports]
                imports.extend(temp_list)
    return imports


def get_all_qtqml_modules(qt_quick_control_styles: None | list[str] = None) -> dict[str, QtQmlModuleInfo]:
    """
    Get all qtqml dll files
    Args:
        qt_quick_control_styles: QtQuick.Control styles that are used
    Returns:
        dict: key is module fullname, value is the module info of the qtqml module
    """
    if "QmlImportsPath" in qt.pyside6_library_info.location:
        qml_src_dir = qt.pyside6_library_info.location["QmlImportsPath"]
    else:
        qml_src_dir = qt.pyside6_library_info.location["Qml2ImportsPath"]
    qml_modules = {}
    folders = []
    for qml_plugin_file in misc.dlls_in_subdirs(qml_src_dir):
        folders.append([os.path.dirname(qml_plugin_file), os.path.normpath(qml_plugin_file)])
    for dirpath, dll_file in folders:
        qmldir_path = os.path.normpath(os.path.join(dirpath, "qmldir"))
        with open(qmldir_path, "r", encoding="utf-8") as f:
            content = f.read()
        # match: module <ModuleIdentifier>
        pattern = re.compile(r"^module\s+(\S+)", re.M)
        result = pattern.findall(content)
        assert len(result) == 1, content
        module_name = result[0]
        # match: import <ModuleIdentifier> [auto]
        import_pattern = re.compile(r"^import\s+([a-zA-Z][a-zA-Z0-9_\.]*)\s*", re.M)
        import_modules = import_pattern.findall(content)
        if module_name == "QtQuick.Controls" and qt_quick_control_styles:
            for style in qt_quick_control_styles:
                # QtQuick.Controls submodules that are implicitly used by the application
                import_modules.append(f"QtQuick.Controls.{style}")
        info = QtQmlModuleInfo(module_name, dll_file, qmldir_path, import_modules)
        qml_modules[module_name] = info
    return qml_modules


def collect_needed_qtqml_files(dir_path: str, qt_quick_control_styles: None | list[str] = None) -> set[QtQmlModuleInfo]:
    """
    Collect qtqml dll files that are needed
    Args:
        dir_path (str): root directory path
        qt_quick_control_styles: QtQuick.Control styles that are used
    Returns:
        All needed QtQmlModuleInfo
    """
    used_qml_module_names = get_used_qml_module_names(dir_path)
    qtqml_modules = get_all_qtqml_modules(qt_quick_control_styles)
    if qt_quick_control_styles:
        for style in qt_quick_control_styles:
            fullname = f"QtQuick.Controls.{style}"
            assert fullname in qtqml_modules, f"{fullname} is not a QtQml module"
            dirname = os.path.dirname(qtqml_modules[fullname].module_path)
            # Some extra QtQml modules are used by QtQuick.Controls
            # They are written in the qml files under the corresponding folder
            implicitly_used = get_used_qml_module_names(dirname)
            for module_name in implicitly_used:
                if module_name not in used_qml_module_names:
                    used_qml_module_names.append(module_name)
    imported_module_names = set()
    result = set()

    def process_qtqml_import(module_names: list[str]) -> None:
        if not module_names:
            return
        todo: list[str] = []
        for module_name in module_names:
            if module_name in imported_module_names:
                continue
            module_info = qtqml_modules.get(module_name)
            if not module_info:
                print(f"QtQml module '{module_name}' doesn't have a corresponding dll", file=sys.stdout)
                continue
            print(f"Using QtQml module '{module_name}', it imports these QtQml modules: {module_info.import_modules}")
            result.add(module_info)
            imported_module_names.add(module_name)
            todo.extend(module_info.import_modules)
        process_qtqml_import(todo)

    # Get QtQml modules that are explicitly or implicitly needed
    # Save results to local variable: result
    process_qtqml_import(used_qml_module_names)
    return result


def collect_qt_webengine_extra_files() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """
    Collect Qt WebEngine extra files:
    QtWebEngineProcess
    resources
    translations
    Returns:
        tuple: binaries, datas
    """
    binaries = []
    datas = []
    locales = "qtwebengine_locales"
    resources = "resources"
    # Translations
    locales_dir = os.path.join(qt.pyside6_library_info.location["TranslationsPath"], locales)
    for root, _, file_names in os.walk(locales_dir):
        for file_name in file_names:
            fullpath = os.path.join(root, file_name)
            datas.append(
                (
                    fullpath,
                    os.path.join(qt.pyside6_library_info.qt_rel_dir, "translations", locales),
                )
            )
    # Resources
    resources_dir = os.path.join(qt.pyside6_library_info.location["DataPath"], resources)
    for root, _, file_names in os.walk(resources_dir):
        for file_name in file_names:
            fullpath = os.path.join(root, file_name)
            datas.append(
                (
                    fullpath,
                    os.path.join(qt.pyside6_library_info.qt_rel_dir, resources),
                )
            )
    # Helper process executable (QtWebEngineProcess), located in ``LibraryExecutablesPath``.
    dest = os.path.join(
        qt.pyside6_library_info.qt_rel_dir,
        os.path.relpath(qt.pyside6_library_info.location["LibraryExecutablesPath"], qt.pyside6_library_info.location["PrefixPath"]),
    )
    binaries.append((os.path.join(qt.pyside6_library_info.location["LibraryExecutablesPath"], "QtWebEngineProcess.exe"), dest))
    return binaries, datas


def normalize_pyi_toc(entry: str, typecode: str, level: int = 1, dest: None | str = None) -> tuple[str, str, str]:
    """
    Return PyInstaller TOC with the input string list
    PyInstaller TOC: destination_path, source_path, typecode ("BINARY" / "DATA")
    """
    if dest is None:
        up_to = [".." for _ in range(level)]
        start_from = os.path.normpath(os.path.join(entry, *up_to))
        dest = os.path.relpath(entry, start_from)
    src = os.path.abspath(entry)
    return (dest, src, typecode)


def process_pyside6_files(assemble_info: AssembleInfo) -> set[str, str]:
    """
    Process PySide6 files
    """
    imported_module_names = set()
    binaries = set()
    datas = set()

    def process_pyside6_import(module_names: list[str]) -> None:
        if not module_names:
            return
        todo: list[str] = []
        for module_name in module_names:
            if module_name in imported_module_names:
                continue
            hook = import_pyi_pyside6_hooks(module_name)
            todo.extend(hook.hiddenimports)
            binaries.update(hook.binaries)
            datas.update(hook.datas)
            imported_module_names.add(module_name)

            module = importlib.import_module(module_name)
            assert isinstance(module.__loader__, machinery.ExtensionFileLoader)
            module_file = module.__file__
            start_from = os.path.normpath(os.path.join(module_file, "..", ".."))
            dest = os.path.relpath(module_file, start_from)
            dest_dir = os.path.normpath(os.path.join(dest, ".."))
            binaries.add((module_file, dest_dir))
        process_pyside6_import(todo)

    # Get PySide6 modules that are explicitly or implicitly needed
    # Save results to local variables: binaries, datas
    process_pyside6_import(assemble_info.pyside6_modules)

    if is_qtquick_application(assemble_info):
        qtqml_modules = collect_needed_qtqml_files(assemble_info.qml_directory, assemble_info.qt_quick_control_styles)
    else:
        qtqml_modules = set()
    # Get binaries and datas that are not needed
    all_qtqml_modules = get_all_qtqml_modules()
    all_qtqml_binaries = set()
    all_qtqml_datas = set()
    qtqml_binaries = set()
    qtqml_datas = set()
    for qtqml_module in qtqml_modules:
        qtqml_binaries.add(qtqml_module.module_path)
        qtqml_datas.add(qtqml_module.qmldir_path)
    for qtqml_module in all_qtqml_modules.values():
        all_qtqml_binaries.add(qtqml_module.module_path)
        all_qtqml_datas.add(qtqml_module.qmldir_path)
    dont_need_binaires = all_qtqml_binaries - qtqml_binaries
    dont_need_datas = all_qtqml_datas - qtqml_datas

    # Filter binaries and datas that are not needed
    result_binaries = []
    result_datas = []
    used_web_engine = False
    for src, dest_dir in binaries:
        src = os.path.normpath(src)
        if src in dont_need_binaires:
            continue
        result_binaries.append((src, dest_dir))
        if "WebEngine" in src:
            used_web_engine = True
    for src, dest_dir in datas:
        src = os.path.normpath(src)
        if src in dont_need_datas:
            continue
        result_datas.append((src, dest_dir))

    if used_web_engine:
        web_engine_binaries, web_engine_datas = collect_qt_webengine_extra_files()
        result_binaries.extend(web_engine_binaries)
        result_datas.extend(web_engine_datas)

    # Copy all Qt binaries and datas to the output directory
    for src, dest_dir in itertools.chain(result_binaries, result_datas):
        if os.path.isdir(src):
            continue
        if src.endswith((".qml", ".qmltypes", ".js")):
            continue
        dest_dir = os.path.join(assemble_info.output_directory, dest_dir)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        try:
            shutil.copy(src, dest_dir)
        except FileExistsError:
            # File is already there, skip it.
            pass
    return result_binaries


def assemble_application(assemble_info: AssembleInfo) -> None:
    """
    Assemble application
    """
    # First clear the output directory
    if os.path.isdir(assemble_info.output_directory):
        shutil.rmtree(assemble_info.output_directory)
    os.makedirs(assemble_info.output_directory)

    # Initialize binaries with user inputs
    pyi_binaries = [normalize_pyi_toc(binary, "BINARY") for binary in assemble_info.binaries]

    # Analyze which modules are used to run the application
    analysis_info = generate_frozen_modules.ModuleAnalysisInfo(
        assemble_info.entry_module_name, assemble_info.hidden_imports, assemble_info.excludes
    )
    modules = generate_frozen_modules.analyze_module(
        analysis_info, generate_frozen_modules.ModuleType.EXTENSION_MODULE | generate_frozen_modules.ModuleType.SOURCE_MODULE
    )

    # Process PySide6 files, get which PySide6 binaries is used by the application
    # And append then to the PyInstaller binaries
    # This should be done before calling build_main.find_binary_dependencies
    # Because some QtQml modules depend on some extra Qt modules, such as Qt6QmlModels.dll
    pyside6_binaries = process_pyside6_files(assemble_info)
    for src, _ in pyside6_binaries:
        if os.path.isdir(src):
            continue
        for site_packages_dir in site.getsitepackages():
            if src.startswith(site_packages_dir):
                relpath = os.path.relpath(src, site_packages_dir)
                if not relpath.startswith("PySide6"):
                    continue
                pyi_binaries.append(normalize_pyi_toc(src, "BINARY", dest=relpath))

    # Process extension binaries
    platform_dynload_dir = get_platform_dynload_dir()
    for module_name, module in modules.items():
        if not module.__file__.endswith(tuple(machinery.EXTENSION_SUFFIXES)):
            continue
        if module.__file__.startswith(platform_dynload_dir):
            if assemble_info.ignore_platform_dynload:
                continue
        level = module_name.count(".") + 1
        file_basename = os.path.basename(module.__file__)
        if "__init__" in file_basename:
            # __init__.pyd
            level += 1
        pyi_binaries.append(normalize_pyi_toc(module.__file__, "BINARY", level))

    # Get all dependencies of the binaries using PyInstaller's API
    import_packages = sorted(modules.keys())
    dependencies = build_main.find_binary_dependencies(pyi_binaries, import_packages)

    pyi_datas = []
    for data in assemble_info.datas:
        relpath = os.path.relpath(data, generate_frozen_modules.ROOT_DIR)
        pyi_datas.append(normalize_pyi_toc(data, "DATA", dest=relpath))

    # konoha-specific
    import blib2to3  # pylint: disable=import-outside-toplevel

    blib2to3_path = os.path.dirname(blib2to3.__file__)
    grammar_path = os.path.join(blib2to3_path, "Grammar.txt")
    grammar_relpath = os.path.join("blib2to3", "Grammar.txt")
    pyi_datas.append(normalize_pyi_toc(grammar_path, "DATA", dest=grammar_relpath))
    pattern_grammar_path = os.path.join(blib2to3_path, "PatternGrammar.txt")
    pattern_grammar_relpath = os.path.join("blib2to3", "PatternGrammar.txt")
    pyi_datas.append(normalize_pyi_toc(pattern_grammar_path, "DATA", dest=pattern_grammar_relpath))

    # Copy all binaries and datas to the output directory
    for dest, src, _ in itertools.chain(dependencies, pyi_datas):
        if re.match(r"py(?:thon(?:com(?:loader)?)?|wintypes)\d+\.dll", dest):
            # python3.dll, python311.dll, python312.dll, etc.
            if not src.startswith(generate_frozen_modules.ROOT_DIR) and assemble_info.static_python:
                continue
        dest = os.path.join(assemble_info.output_directory, dest)
        dirname = os.path.dirname(dest)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        shutil.copyfile(src, dest)


def main() -> None:
    """
    Entry point
    Returns:
        None
    """
    assemble_info = AssembleInfo("", "", [], [], [], [], [], [])
    if len(sys.argv) < 2:
        generate_frozen_modules.usage("Need at least 1 argument to assemble application.")
    for arg in sys.argv[1:]:
        if arg.startswith("--hidden-imports"):
            hidden_imports = generate_frozen_modules.get_list_arg(arg, "--hidden-imports")
            assemble_info.hidden_imports = hidden_imports
        elif arg.startswith("--excludes"):
            excludes = generate_frozen_modules.get_list_arg(arg, "--excludes")
            assemble_info.excludes = excludes
        elif arg.startswith("--binaries"):
            binaries = generate_frozen_modules.get_list_arg(arg, "--binaries")
            assemble_info.binaries = binaries
        elif arg.startswith("--datas"):
            datas = generate_frozen_modules.get_list_arg(arg, "--datas")
            assemble_info.datas = datas
        elif arg.startswith("--pyside6-modules"):
            pyside6_modules = generate_frozen_modules.get_list_arg(arg, "--pyside6-modules")
            assemble_info.pyside6_modules = pyside6_modules
        elif arg.startswith("--qt-quick-control-styles"):
            qt_quick_control_stypes = generate_frozen_modules.get_list_arg(arg, "--qt-quick-control-styles")
            assemble_info.qt_quick_control_styles = qt_quick_control_stypes
        elif arg.startswith("--dont-ignore-platform-dynload"):
            assemble_info.ignore_platform_dynload = False
        elif arg.startswith("--dynamic-python"):
            assemble_info.static_python = False
        elif arg.startswith("--qml-directory"):
            datas = generate_frozen_modules.get_list_arg(arg, "--qml-directory")
            assemble_info.qml_directory = datas[0]
        else:
            assemble_info.entry_module_name = arg
    if not assemble_info.qml_directory and is_qtquick_application(assemble_info):
        generate_frozen_modules.usage("Need to specify --qml-directory")
    assemble_application(assemble_info)


if __name__ == "__main__":
    main()
