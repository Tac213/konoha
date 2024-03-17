# Konoha

Visual scripting editor based on Python.

## Prerequisites

-   Git 2.32 (or more recent)
-   Python 3.11.0 (or more recent)
-   Visual Studio 2022 (deployment only)
-   CMake (deployment only)
-   Ninja (deployment only)

## Development

Recommended IDE: [Visual Studio Code](https://code.visualstudio.com/)

To setup Development Environment, run the following commands:

```bash
# git clone this repository
cd konoha
# create venv
python3 -m venv .venv
# activate venv
source .venv/bin/activate
# for Windows Command Prompt, run the following command to activate venv
# .venv\Scripts\activate.bat
# for Windows Powershell, run the following command to activate venv
# .venv\Scripts\Activate.ps1
# for Winows Git Bash, run the following command to activate venv
# source .venv/Scripts/activate

# install packages
pip3 install -e ".[dev]"
# generate snake_case and true_property pyi for VSCode
pyside6-genpyi all --feature snake_case true_property
# deactivate venv
deactivate
# open current folder using VSCode
code .
```

After opening the folder, click `Yes` when VSCode ask you whether to install the recommended extensions.

The next step is to select the interpreter under `.venv` folder as the development interpreter. Simply press `Ctrl + Shift + P`, then enter `Python: Select Interpreter` command.

Finally, press `F5`. The application should be launched in debug mode.

To test the application, write a simple python script like this:

```python
# I'm comment
print("Hello world!")
```

Now try to open this script with the konoha application.

## Deployment

Currently only Windows is supported.

To deploy the application, simply press `Ctrl + P` in VSCode, then enter `task Deploy(Release)`, if the task is performed successfully, the application will be deployed under: `${workspaceFolder}/deployment`.

If you want to deploy the Debug version, debugpy will suspend the process while performing the `Configure Debug Frozen`. When you see the output log of debugpy, start the `Attach Python` debug configuration. The process will continue to run as soon as you attach to the process.
