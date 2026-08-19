# tools/autoupdater.py

import os
import sys
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

    installer_url = None
    for asset in assets:
        if asset.get("name", "").lower().endswith("-setup.exe"):
            installer_url = asset.get("browser_download_url")
            break

    if not installer_url:
        print("no installer asset found in latest release")
        return None, None

    return tag_name, installer_url


def parse_version(v):
    v = v.strip().lstrip("vV")
    parts = v.split(".")
    result = []
    for p in parts:
        digits = "".join(c for c in p if c.isdigit())
        result.append(int(digits) if digits else 0)
    return tuple(result)


def check_for_update(local_version):
    tag_name, installer_url = get_latest_release()
    if tag_name is None:
        return False, None, None

    remote = parse_version(tag_name)
    local = parse_version(local_version)

    return (remote > local), tag_name, installer_url


def perform_update(installer_url):
    print("downloading update...")
    try:
        tempdir = tempfile.mkdtemp(prefix="caysmnlauncher_update_")
        installer_path = os.path.join(tempdir, "cayymnlauncher-setup.exe")
        response = requests.get(installer_url, stream=True, timeout=30)
        response.raise_for_status()
        with open(installer_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
    except requests.RequestException as e:
        print(f"failed to download update: {e}")
        return False

    print("launching installer...")
    subprocess.Popen(
        [installer_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
        creationflags=(
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    )
    sys.exit()