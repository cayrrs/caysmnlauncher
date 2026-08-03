# if ima be honest i did NOT make this script
# just modified it


import ctypes
from ctypes import wintypes
import subprocess
import os

SW_HIDE = 0
SEE_MASK_NOCLOSEPROCESS = 0x00000040
INFINITE = 0xFFFFFFFF


class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", wintypes.HWND),
        ("lpVerb", ctypes.c_wchar_p),
        ("lpFile", ctypes.c_wchar_p),
        ("lpParameters", ctypes.c_wchar_p),
        ("lpDirectory", ctypes.c_wchar_p),
        ("nShow", ctypes.c_int),
        ("hInstApp", ctypes.c_void_p),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", ctypes.c_wchar_p),
        ("hkeyClass", ctypes.c_void_p),
        ("dwHotKey", wintypes.DWORD),
        ("hIcon", ctypes.c_void_p),
        ("hProcess", ctypes.c_void_p),
    ]


def run_elevated(command: str) -> int:
    params = f'-NoProfile -WindowStyle Hidden -Command "{command}"'

    sei = SHELLEXECUTEINFO()
    sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
    sei.fMask = SEE_MASK_NOCLOSEPROCESS
    sei.hwnd = None
    sei.lpVerb = "runas"
    sei.lpFile = "powershell.exe"
    sei.lpParameters = params
    sei.lpDirectory = None
    sei.nShow = SW_HIDE
    sei.hInstApp = None

    if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei)):
        return -1

    handle = sei.hProcess
    ctypes.windll.kernel32.WaitForSingleObject(handle, INFINITE)

    exit_code = wintypes.DWORD()
    ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
    ctypes.windll.kernel32.CloseHandle(handle)

    return exit_code.value


def add_defender_exclusion(target_dir: str) -> bool:
    target_dir = os.path.abspath(target_dir)
    if not os.path.isdir(target_dir):
        print(f"Error: directory does not exist: {target_dir}")
        return False

    command = f'Add-MpPreference -ExclusionPath \\"{target_dir}\\"'
    code = run_elevated(command)

    if code == -1:
        print("Elevation was declined or failed to launch.")
        return False
    if code != 0:
        print(f"Command finished with exit code {code}.")
        return False

    print(f"Exclusion added for: {target_dir}")
    return True


def verify_exclusion(target_dir: str) -> bool:
    target_dir = os.path.abspath(target_dir)
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-MpPreference).ExclusionPath"],
        capture_output=True,
        text=True,
    )
    paths = [p.strip() for p in result.stdout.splitlines() if p.strip()]
    return any(target_dir.lower() == p.lower() for p in paths)