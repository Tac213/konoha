"""
Script for code signing
"""

import sys
import os
import subprocess

from qt_quick_python_tools import deploy_utils

_COMPANY_NAME = "Tac Uchiha"
_SELF_CERTIFICATE_PASSWORD = "coDeSIgN#Tac*Uchiha}"
_SELF_CERTIFICATE_FILE_NAME = "certificate.pfx"


def _write_self_sign_cert_ps(dir_path: str, friendly_name: str) -> str:
    """
    https://learn.microsoft.com/en-us/windows/msix/package/create-certificate-package-signing
    https://learn.microsoft.com/en-us/powershell/module/pki/new-selfsignedcertificate
    """
    ps1_path = os.path.join(dir_path, "create-self-sign-certificate.ps1")
    if os.path.exists(ps1_path):
        return ps1_path
    with open(ps1_path, "w", encoding="utf-8") as fp:
        fp.write(
            f"""\
$params = @{{
    Type = 'Custom'
    Subject = 'E=cookiezhx@163.com,CN={_COMPANY_NAME}'
    TextExtension = @(
        '2.5.29.37={{text}}1.3.6.1.5.5.7.3.3',
        '2.5.29.17={{text}}email=cookiezhx@163.com' )
    KeyUsage = 'DigitalSignature'
    CertStoreLocation = 'Cert:\\CurrentUser\\My'
    FriendlyName = '{friendly_name}'
}}
$cert = New-SelfSignedCertificate @params
$password = ConvertTo-SecureString -String "{_SELF_CERTIFICATE_PASSWORD}" -Force -AsPlainText
Export-PfxCertificate -cert $cert -FilePath {_SELF_CERTIFICATE_FILE_NAME} -Password $password
"""
        )
    return ps1_path


def sign_file_win32(file_to_sign: str) -> None:
    """
    Sign file on win32
    https://gist.github.com/PaulCreusy/7fade8d5a8026f2228a97d31343b335e
    https://www.youtube.com/watch?v=m77p30bvY5E
    """
    signtool_exe = "C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit\\signtool.exe"
    if not os.path.exists(signtool_exe):
        usage("You haven't installed Windows SDK, couldn't sign file.")
    file_to_sign = os.path.abspath(file_to_sign)
    if not os.path.exists(file_to_sign):
        usage(f"File doesn't exist: {file_to_sign}")
    stdout = deploy_utils.LogPipe(print)
    stderr = deploy_utils.LogPipe(lambda msg: print(msg, file=sys.stderr))
    dir_path = os.path.dirname(file_to_sign)
    pfx_file_path = os.path.join(dir_path, _SELF_CERTIFICATE_FILE_NAME)
    if not os.path.exists(pfx_file_path):
        file_basename = os.path.basename(file_to_sign)
        friendly_name, _ = os.path.splitext(file_basename)
        ps1_path = _write_self_sign_cert_ps(dir_path, friendly_name)
        with subprocess.Popen(["powershell.exe", ps1_path], stdout=stdout, stderr=stderr, cwd=dir_path) as p:
            p.wait()
            if p.returncode:
                stdout.close()
                stderr.close()
                sys.exit(p.returncode)
    with subprocess.Popen(
        [
            signtool_exe,
            "sign",
            "/v",
            "/f",
            pfx_file_path,
            "/p",
            _SELF_CERTIFICATE_PASSWORD,
            "/fd",
            "SHA256",
            "/tr",
            "http://timestamp.digicert.com/",
            "/td",
            "SHA256",
            file_to_sign,
        ],
        stdout=stdout,
        stderr=stderr,
    ) as p:
        p.wait()
        stdout.close()
        stderr.close()
        if p.returncode:
            sys.exit(p.returncode)


def main() -> None:
    """
    Entry point
    Returns:
        None
    """
    if sys.platform.startswith("win32"):
        sign_file_win32(*sys.argv[1:])
    else:
        usage(f"Unsupported platform: {sys.platform}")


def usage(msg: str) -> None:
    """
    Print message and exit
    Args:
        msg: message to show
    Returns:
        None
    """
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
