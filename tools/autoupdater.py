# tools/autoupdater.py

import os
import sys
import zipfile
import shutil
import tempfile
import subprocess
import requests


API_URL = f"https://api.github.com/repos/cayrrs/caysmnlauncher/releases/latest"


def get_latest_release():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"failed to check for updates: {e}")
        return None, None

    tag_name = data.get("tag_name")
    assets = data.get("assets", [])

    zip_url = None
    for asset in assets:
        if asset.get("name", "").lower().endswith(".zip"):
            zip_url = asset.get("browser_download_url")
            break

    if not zip_url:
        print("no zip asset found in latest release")
        return None, None

    return tag_name, zip_url


def parse_version(v):
    v = v.strip().lstrip("vV")
    parts = v.split(".")
    result = []
    for p in parts:
        digits = "".join(c for c in p if c.isdigit())
        result.append(int(digits) if digits else 0)
    return tuple(result)


def check_for_update(local_version):
    tag_name, zip_url = get_latest_release()
    if tag_name is None:
        return False, None, None

    remote = parse_version(tag_name)
    local = parse_version(local_version)

    return (remote > local), tag_name, zip_url


def download_update(zip_url):
    tempdir = tempfile.mkdtemp(prefix="caysmnlauncher_update_")
    destpath = os.path.join(tempdir, "update.zip")

    response = requests.get(zip_url, stream=True, timeout=30)
    response.raise_for_status()
    with open(destpath, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)

    return destpath


def perform_update(zip_url):
    exepath = os.path.abspath(sys.argv[0])
    launcherdir = os.path.dirname(exepath)             
    launcherparentdir = os.path.dirname(launcherdir)   
    stagingdir = os.path.join(launcherparentdir, "cayymnlauncher_new")
    exename = os.path.basename(exepath)
    logfile = os.path.join(tempfile.gettempdir(), "caysmnlauncher_update_log.txt")

    print("downloading update...")
    try:
        zippath = download_update(zip_url)
    except requests.RequestException as e:
        print(f"failed to download update: {e}")
        return False

    print("extracting update...")
    if os.path.isdir(stagingdir):
        shutil.rmtree(stagingdir, ignore_errors=True)
    os.makedirs(stagingdir, exist_ok=True)

    with zipfile.ZipFile(zippath, 'r') as zip:
        zip.extractall(stagingdir)

    if not os.listdir(stagingdir):
        print("update zip appears empty, aborting")
        shutil.rmtree(stagingdir, ignore_errors=True)
        return False

    batchpath = os.path.join(tempfile.gettempdir(), "caysmnlauncher_update.bat")
    with open(batchpath, "w") as f:
        f.write(f"""@echo off
set "launcherdir={launcherdir}"
set "stagingdir={stagingdir}"
set "exename={exename}"
set "logfile={logfile}"

timeout /t 2 /nobreak >nul

set count=0
:deleteloop
if not exist "%launcherdir%" goto movestep
set /a count+=1
if %count% gtr 30 (
    echo failed to delete old launcher folder >> "%logfile%"
    goto end
)
rmdir /s /q "%launcherdir%" 2>>"%logfile%"
timeout /t 1 /nobreak >nul
goto deleteloop

:movestep
move "%stagingdir%" "%launcherdir%" >>"%logfile%" 2>&1
start "" "%launcherdir%\\%exename%"

:end
del "%~f0"
""")

    subprocess.Popen(
        ["cmd.exe", "/c", batchpath],
        creationflags=(
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    )

    return True