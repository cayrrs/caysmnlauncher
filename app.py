from tools.launchtokengenerator import writelaunchtoken
import os
import requests
import time
import sys
from zipfile import ZipFile
import shutil
import subprocess
from pyshortcuts import make_shortcut
import tkinter as tk
from tkinter import filedialog
import json
import tools.autoupdater

root = tk.Tk()
root.withdraw()

# variables

LAUNCHER_VERSION = "v1.0.3" 

localappdata = os.getenv('LOCALAPPDATA')
launcherappdata = os.path.join(localappdata, "cayymnlauncher")
meownetappdata = os.path.join(localappdata, "MeowNet")
rootenv = os.getenv('SystemDrive')
root = os.path.join(rootenv, os.sep)
gamedirectory = os.path.join(root, "Meow.Net")
game_download_link = "https://cdn.cookedasset.com/build/Meow_Beta.zip" 
launchmode = "vr"
exepath = os.path.abspath(sys.argv[0])
updateurl = "https://meowii.app/LastUpdate"


# helper functions

def clearconsole():
    os.system("cls")


def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunk_size = 1024 * 256  

    start_time = time.time()
    last_update = start_time

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)

            now = time.time()
            if now - last_update >= 0.2:  
                elapsed = now - start_time
                speed_mbps = (downloaded * 8 / elapsed) / 1_000_000  
                percent = (downloaded / total_size * 100) if total_size else 0

                sys.stdout.write(
                    f"\r{percent:5.1f}%  "
                    f"{downloaded / (1024*1024):8.2f} MB / {total_size / (1024*1024):.2f} MB  "
                    f"{speed_mbps:6.2f} Mbps"
                )
                sys.stdout.flush()
                last_update = now

    print()  
    return dest_path


def extractzip(zipfile, destination):
    with ZipFile(zipfile, 'r') as zip:
        zip.extractall(destination)

def readsettings(string):
    with open(settingsfile, 'r') as file:
        data = json.load(file)
        if string:
            parseddata = data[string]
            return parseddata
        else:
            return data

def writesettings(key, data):
    existingdata = readsettings(None)
    if key in existingdata:
        existingdata[key] = data 
        with open(settingsfile, 'w') as file:
            json.dump(existingdata, file, indent=4)


# main stuff


def makeshortcut():
    make_shortcut(
        script=exepath,
        name= "MeowNet Launcher",
        icon=exepath,
        desktop=True,
        startmenu=True,
        terminal=True
    )


def updatecheck():
    clearconsole()
    print("checking for meow.net updates..")
    webupdatevar = requests.get(updateurl).json()
    updatefile = os.path.join(gamedirectory, "last_update.txt")
    f = open(updatefile, 'r')
    localupdate = f.read()
    if webupdatevar["last_update"] != localupdate:
        print("a new build of meow.net is available, would you like to update?")
        updatechoice = input("y/n")
        if updatechoice in ("", "y", "yes"):
            print("updating game...")
            installgame(True)




def installgame(isupdate):
    clearconsole()
    print("creating temporary folder..")
    os.makedirs(os.path.join(parentdirectory, "installer_temp"), exist_ok=True)
    print("downloading latest version of meow.net...")
    destpath = download_file(game_download_link, os.path.join(parentdirectory, "installer_temp", "Meow_Beta.zip"))
    print("\n finished downloading meow.net")
    print("\n extracting Meow_Beta.zip... (this may take some time)")
    extractzip(destpath, parentdirectory)
    if os.path.isdir(gamedirectory):
        print("extracted successfully!")
        print("cleaning up..")
        shutil.rmtree(os.path.join(parentdirectory, "installer_temp"), ignore_errors=True)
        print("fixing last_update.txt")
        webupdatevar = requests.get(updateurl).json()
        with open(os.path.join(gamedirectory, "last_update.txt"), "w", encoding="utf-8") as f:
                f.write(webupdatevar["last_update"])
        clearconsole()
        if isupdate:
            return True
        else:
            print("it is HIGHLY recommended that you add a Windows Defender exclusion for meow.net yourself.")
            print(f"folder to exclude: {gamedirectory}")
            print("Windows Settings > Privacy & Security > Windows Security > Virus & threat protection")
            print("  > Manage settings > Add or remove exclusions > Add an exclusion > Folder")
            print("without one, defender can delete the patch and you'll need to reinstall to fix it.")
            print("this can be reverted at any time from the same menu.")

        return True
    else:
        return False
    


def movegame():
    global gamedirectory
    global parentdirectory
    newfolderpath = filedialog.askdirectory(title="new meow.net directory")
    if newfolderpath:
        oldgamedirectory = gamedirectory
        newgamedirectory = os.path.join(newfolderpath, "Meow.Net")
        print(f"selected folder: {newfolderpath}")
        shutil.move(gamedirectory, newfolderpath)
        print("finished moving files")
        print("writing new settings data..")
        gamedirectory = newgamedirectory
        parentdirectory = os.path.dirname(os.path.normpath(gamedirectory))
        writesettings("customdirectory", os.path.join(newfolderpath, "Meow.Net"))
        print("if you had a Defender exclusion set for the old location, remove it yourself:")
        print(f"  old folder: {oldgamedirectory}")
        print("and add a new one for the new location:")
        print(f"  new folder: {gamedirectory}")
        print("Windows Settings > Privacy & Security > Windows Security > Virus & threat protection")
        print("  > Manage settings > Add or remove exclusions")
    else:
        print("no folder selected")
        return

def checkforlauncherupdate():
    print("checking for launcher updates...")
    available, tag_name, zip_url = tools.autoupdater.check_for_update(LAUNCHER_VERSION)
    if available:
        print(f"a new launcher version is available: {tag_name} (current: {LAUNCHER_VERSION})")
        choice = input("update now? y/n ").strip().lower()
        if choice in ("", "y", "yes"):
            if tools.autoupdater.perform_update(zip_url):
                print("update staged, restarting...")
                sys.exit()
            else:
                print("update failed, continuing with current version")
    else:
        print("launcher is up to date")



def init():
    global settingsfile
    global gamedirectory
    global parentdirectory
    checkforlauncherupdate()
    print("creating required directories..")
    if os.path.isdir(meownetappdata):
        print("meownet app data found")
    else:
        print("meownet app data not found, making")
        os.mkdir(meownetappdata)

    if os.path.isdir(launcherappdata):
        print("launcher app data found")
    else:
        print("launcher app data not found, making")
        os.mkdir(launcherappdata)
        print("making config file")
        settingsfile = os.path.join(launcherappdata, "settings.json")
        basesettings = {'customdirectory': None}
        with open(settingsfile, 'x') as file:
            json.dump(basesettings, file)

    settingsfile = os.path.join(launcherappdata, "settings.json")
    customdirectory = readsettings("customdirectory")
    if customdirectory:
        gamedirectory = customdirectory
    else:
        print("no custom directory found")
    parentdirectory = os.path.dirname(os.path.normpath(gamedirectory))
    print("checking for pre-existing game install..")
    if os.path.isdir(gamedirectory):
        print("game install found!")
        updatecheck()
        return
    else:
        print("\n \n game install not found, do you want to install? \n declining this will close the launcher.")
        consent = input("\n y/n? ").strip().lower()
        if consent in ("y", "yes"):
            print("continuing")
            if installgame(False):
                clearconsole()
                print("Meow.net installed!")
                print("Going to menu!")
                time.sleep(1)
                return
            else:
                clearconsole()
                print("install game failed, restart the launcher")

        else:
            sys.exit()


def repairgame():
    global parentdirectory

    print("Uninstalling Meow.Net...")
    parentdirectory = os.path.dirname(os.path.normpath(gamedirectory))
    shutil.rmtree(gamedirectory, ignore_errors=True)
    print("Uninstalled Meow.Net")
    print("Beginning installation")
    if installgame(True):
        print("Successfully repaired Meow.Net!")
        return
    else:
        print("Failed to repair Meow.Net!")
        time.sleep(3)
        return
    

def gameintegcheck():
    if os.path.isdir(os.path.join(gamedirectory, "BepInEx", "plugins")) & os.path.isfile(os.path.join(gamedirectory, "BepInEx", "plugins", "WoofPatch.dll")):
        return True
    else:
        return False



def launch_game():
    clearconsole()
    print("checking game integrity")
    if gameintegcheck():
        print("passed integ check")
    else:
        print("Didn't pass integrity check. Do you want to repair Meow.Net? Not repairing will result in the game being in a broken state.")
        choice = input("y/n? ")
        if choice in ["yes", "y", ""]:
            clearconsole()
            repairgame()
    print("launching Meow.Net!")
    writelaunchtoken(os.path.join(meownetappdata, "launch.token"))
    exe_path = os.path.join(gamedirectory, "RecRoom.exe")
    args = [f"+forcemode:{launchmode}", "-noeac"]
    subprocess.Popen(
        [exe_path] + args,
        cwd=gamedirectory,
        creationflags=(
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_BREAKAWAY_FROM_JOB
        )
    )
    input("Press enter to close launcher..")
    sys.exit()



def showmenu():
    clearconsole()
    print("cay's meownet launcher")
    print("made by @cayrr.s <3")
    print("\n\n\n")
    print("1. Launch Meow.Net")
    print(f"2. Change Launch Mode  current: {launchmode}")
    print("3. Make desktop shortcut")
    print(f"4. Change install location   current location: {gamedirectory}")
    print("5. Repair Meow.Net")
    print("\n")
    


def main():
    global launchmode

    while True:
        showmenu()
        choice = input("Enter a choice: ")
        if choice == "1":
            launch_game()
        if choice == "2":
            if launchmode == "vr":
                launchmode = "screen"
            else:
                launchmode = "vr"
        if choice == "3":
            clearconsole()
            makeshortcut()
            print("Made desktop shortcut!")
            time.sleep(1)
        if choice == "4":
            clearconsole()
            movegame()
        if choice == "5":
            clearconsole()
            repairgame()





init()
main()