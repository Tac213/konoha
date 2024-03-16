#include <cstdlib>
#include <string>
#if defined(_DEBUG)
#    undef _DEBUG // https://stackoverflow.com/questions/38860915/lnk2019-error-in-pycaffe-in-debug-mode-for-caffe-for-windows
#endif
#include <Python.h>
#if defined(_MSC_VER)
#    include <Windows.h>
#endif

#if defined(FREEZE_APPLICATION)
#    include <filesystem>
#    include "frozen_modules/frozen_modules.h"
#endif

#define STR_HELPER(x) #x
#define STR(x)        STR_HELPER(x)


static int
pymain_run_module(const wchar_t* modname, int set_argv0)
{
    PyObject *module, *runpy, *runmodule, *runargs, *result;
    if (PySys_Audit("cpython.run_module", "u", modname) < 0)
    {
        PyErr_Print();
        return 1;
    }
    runpy = PyImport_ImportModule("runpy");
    if (runpy == nullptr)
    {
        fprintf(stderr, "Could not import runpy module\n");
        PyErr_Print();
        return 1;
    }
    runmodule = PyObject_GetAttrString(runpy, "_run_module_as_main");
    if (runmodule == nullptr)
    {
        fprintf(stderr, "Could not access runpy._run_module_as_main\n");
        Py_DECREF(runpy);
        PyErr_Print();
        return 1;
    }
    module = PyUnicode_FromWideChar(modname, wcslen(modname));
    if (module == nullptr)
    {
        fprintf(stderr, "Could not convert module name to unicode\n");
        Py_DECREF(runpy);
        Py_DECREF(runmodule);
        PyErr_Print();
        return 1;
    }
    runargs = PyTuple_Pack(2, module, set_argv0 ? Py_True : Py_False);
    if (runargs == nullptr)
    {
        fprintf(stderr, "Could not create arguments for runpy._run_module_as_main\n");
        Py_DECREF(runpy);
        Py_DECREF(runmodule);
        Py_DECREF(module);
        PyErr_Print();
        return 1;
    }
    result = PyObject_Call(runmodule, runargs, nullptr);
    Py_DECREF(runpy);
    Py_DECREF(runmodule);
    Py_DECREF(module);
    Py_DECREF(runargs);
    if (result == nullptr)
    {
        PyErr_Print();
        return 1;
    }
    Py_DECREF(result);
    return 0;
}


#if defined(NEED_CONSOLE)
int main(int argc, char** argv)
#else
int WINAPI
WinMain(HINSTANCE hInst, HINSTANCE hPrevInst, LPSTR lpCmdLine, int nShowCmd) // NOLINT(readability-identifier-naming)
#endif
{
#if !defined(NEED_CONSOLE)
    int    argc = __argc;
    char** argv = __argv;
#endif
#if defined(FREEZE_APPLICATION)
    PyImport_FrozenModules = _PyImport_FrozenModules;
#endif
    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);

#if !defined(FREEZE_APPLICATION)
#    if defined(_MSC_VER)
    char*  env_p = nullptr;
    size_t sz    = 0;
    if (_dupenv_s(&env_p, &sz, "VIRTUAL_ENV") == 0 && env_p != nullptr)
#    else
    if (const char* env_p = std::getenv("VIRTUAL_ENV"))
#    endif // defined(_MSC_VER)
    {
        std::string python_executable = env_p;
#    if defined(_MSC_VER)
        python_executable += "\\Scripts\\python.exe";
        free(env_p);
#    else
        python_executable += "/bin/python";
#    endif // defined(_MSC_VER
        status = PyConfig_SetBytesString(&config, &config.program_name, python_executable.c_str());
        if (PyStatus_Exception(status))
        {
            PyConfig_Clear(&config);
            fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set venv python executable.");
            return 1;
        }
    }
#else  // FREEZE_APPLICATION
    config.module_search_paths_set = 1;                                      // sys.path will be: ['']

    std::filesystem::path executable_path(argv[0]);
    auto                  executable_directory = executable_path.parent_path().wstring();

    config.write_bytecode = 0;

    // In Python3.11, this will not work.
    // See: https://github.com/python/cpython/issues/106718
    status = PyConfig_SetString(&config, &config.stdlib_dir, executable_directory.c_str());
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys._stdlib_dir.");
        return 1;
    }
#endif // !defined(FREEZE_APPLICATION)

    status = PyConfig_SetBytesArgv(&config, argc, const_cast<char* const*>(argv));
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys.argv.");
        return 1;
    }
    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to initialize CPython from config.");
        return 1;
    }

    PyConfig_Clear(&config);

    int exitcode = 0;

#if !defined(FREEZE_APPLICATION)
    exitcode = Py_RunMain();
#else
    // Set sys._stdlib_dir manually
    PyObject *sysmodule, *stdlib_dir_value;

    const auto* stdlibdir = executable_directory.c_str();

    sysmodule = PyImport_ImportModule("sys");
    if (sysmodule == nullptr)
    {
        fprintf(stderr, "Could not import sys module\n");
        PyErr_Print();
        return 1;
    }
    stdlib_dir_value = PyUnicode_FromWideChar(stdlibdir, wcslen(stdlibdir));
    if (stdlib_dir_value == nullptr)
    {
        fprintf(stderr, "Could not convert directory name to unicode\n");
        Py_DECREF(sysmodule);
        PyErr_Print();
        return 1;
    }
    if (PyObject_SetAttrString(sysmodule, "_stdlib_dir", stdlib_dir_value) == -1)
    {
        fprintf(stderr, "Could not set sys._stdlib_dir\n");
        Py_DECREF(sysmodule);
        Py_DECREF(stdlib_dir_value);
        PyErr_Print();
        return 1;
    }
    Py_DECREF(stdlib_dir_value);
    // Set sys.frozen
    if (PyObject_SetAttrString(sysmodule, "frozen", Py_True) == -1)
    {
        fprintf(stderr, "Could not set sys.frozen\n");
        Py_DECREF(sysmodule);
        PyErr_Print();
        return 1;
    }
    Py_DECREF(sysmodule);
    exitcode = pymain_run_module(L"__main__", 0);
#endif // !defined(FREEZE_APPLICATION)

    return exitcode;
}