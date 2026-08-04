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


def check_for_update(local_version):
    tag_name, zip_url = get_latest_release()
    if tag_name is None:
        return False, None, None

    return (tag_name != local_version), tag_name, zip_url


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
    stagingdir = os.path.join(launcherparentdir, "cayymclauncher_new")
    exename = os.path.basename(exepath)

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
timeout /t 2 /nobreak >nul
rmdir /s /q "{launcherdir}"
move "{stagingdir}" "{launcherdir}"
start "" "{os.path.join(launcherdir, exename)}"
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