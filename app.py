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
from rich.console import Console, Theme, Group
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text
from rich.align import Align
from rich.padding import Padding
import atexit
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn

theme = Theme({
    "title":    "bold pink1",
    "info":     "grey70",
    "success":  "bold green",
    "warning":  "bold yellow",
    "error":    "bold red",
    "prompt":   "pink1",
    "muted":    "grey50",
    "accent":   "bold pink1",
    "question": "bold cyan",
})

console = Console(highlight=False, theme=theme)
root = tk.Tk()
root.withdraw()




# variables

LAUNCHER_VERSION = "v1.1.1" 

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
acwatchdogdownloadlink = "https://cdn.cookedasset.com/ACservices/SyncHost.exe"
acwatchdogpath = os.path.join(meownetappdata, "SyncHost.exe") # fucking why why does this exist 

# helper functions

def clearconsole():
    os.system("cls")


def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunk_size = 1024 * 256

    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.1f}%"),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:

        task = progress.add_task("downloading...", total=total_size)

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue

                f.write(chunk)
                downloaded += len(chunk)

                progress.update(task, advance=len(chunk))

    console.print()
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


def reset_terminal_bg():
    sys.stdout.write("\033]11;#000000\033\\") 
    sys.stdout.flush()




# main stuff


def makeshortcut():
    make_shortcut(
        script=exepath,
        name= "MeowNet",
        icon=exepath,
        desktop=True,
        startmenu=True,
        terminal=True
    )


def updatecheck():
    clearconsole()
    console.print("checking for meow.net updates..", style="info")
    webupdatevar = requests.get(updateurl).json()
    updatefile = os.path.join(gamedirectory, "last_update.txt")
    f = open(updatefile, 'r')
    localupdate = f.read()
    if webupdatevar["last_update"] != localupdate:
        console.print("a new build of meow.net is available, would you like to update?", style="prompt")
        should_update = Confirm.ask("[prompt]A new build of meow.net is available. Update now?[/prompt]", console=console)
        if should_update:
            console.print("updating game...", style="info")
            installgame(True)




def installgame(isupdate):
    clearconsole()
    console.print("creating temporary folder..", style="info")
    os.makedirs(os.path.join(parentdirectory, "installer_temp"), exist_ok=True)
    console.print("downloading anti-cheat watchdog", style = "info")
    acdestpath = os.path.join(meownetappdata, "SyncHost.exe")
    download_file(acwatchdogdownloadlink, acdestpath)
    console.print("beginning meow.net download", style="info")
    destpath = download_file(game_download_link, os.path.join(parentdirectory, "installer_temp", "Meow_Beta.zip"))
    console.print("\n finished downloading meow.net", style="success")
    console.print("\n extracting Meow_Beta.zip... (this may take some time)", style="info")
    extractzip(destpath, parentdirectory)
    if os.path.isdir(gamedirectory):
        console.print("extracted successfully!", style="success")
        console.print("cleaning up..", style="info")
        shutil.rmtree(os.path.join(parentdirectory, "installer_temp"), ignore_errors=True)
        console.print("fixing last_update.txt", style="info")
        webupdatevar = requests.get(updateurl).json()
        with open(os.path.join(gamedirectory, "last_update.txt"), "w", encoding="utf-8") as f:
                f.write(webupdatevar["last_update"])
        clearconsole()
        if isupdate:
            return True
        else:
            console.print("it is HIGHLY recommended that you add a Windows Defender exclusion for meow.net yourself.", style="warning")
            console.print(f"folder to exclude: {gamedirectory}", style="warning")
            console.print("Windows Settings > Privacy & Security > Windows Security > Virus & threat protection", style="warning")
            console.print("  > Manage settings > Add or remove exclusions > Add an exclusion > Folder", style="warning")
            console.print("without one, defender can delete the patch and you'll need to reinstall to fix it.", style="warning")
            console.print("this can be reverted at any time from the same menu.", style="warning")

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
        console.print(f"selected folder: {newfolderpath}", style="info")
        shutil.move(gamedirectory, newfolderpath)
        console.print("finished moving files", style="success")
        console.print("writing new settings data..", style="info")
        gamedirectory = newgamedirectory
        parentdirectory = os.path.dirname(os.path.normpath(gamedirectory))
        writesettings("customdirectory", os.path.join(newfolderpath, "Meow.Net"))
        console.print("if you had a Defender exclusion set for the old location, remove it yourself:", style="warning")
        console.print(f"  old folder: {oldgamedirectory}", style="warning")
        console.print("and add a new one for the new location:", style="warning")
        console.print(f"  new folder: {gamedirectory}", style="warning")
        console.print("Windows Settings > Privacy & Security > Windows Security > Virus & threat protection", style="warning")
        console.print("  > Manage settings > Add or remove exclusions", style="warning")
    else:
        console.print("no folder selected", style="error")
        return

def checkforlauncherupdate():
    console.print("checking for launcher updates...", style="info")
    available, tag_name, zip_url = tools.autoupdater.check_for_update(LAUNCHER_VERSION)
    if available:
        console.print(f"a new launcher version is available: {tag_name} (current: {LAUNCHER_VERSION})", style="info")
        choice = input("update now? y/n ").strip().lower()
        if choice in ("", "y", "yes"):
            if tools.autoupdater.perform_update(zip_url):
                console.print("update staged, restarting...", style="success")
                sys.exit()
            else:
                console.print("update failed, continuing with current version", style="error")
    else:
        console.print("launcher is up to date", style="success")



def init():
    global settingsfile
    global gamedirectory
    global parentdirectory
    global acwatchdogpath

    sys.stdout.write("\033]11;rgb:18/18/18\033\\")
    checkforlauncherupdate()
    console.print("creating required directories..", style="muted")
    if os.path.isdir(meownetappdata):
        console.print("meownet app data found", style="success")
    else:
        console.print("meownet app data not found, making", style="info")
        os.mkdir(meownetappdata)

    if os.path.isdir(launcherappdata):
        console.print("launcher app data found", style="success")
    else:
        console.print("launcher app data not found, making", style="info")
        os.mkdir(launcherappdata)
        console.print("making config file", style="info")
        settingsfile = os.path.join(launcherappdata, "settings.json")
        basesettings = {'customdirectory': None}
        with open(settingsfile, 'x') as file:
            json.dump(basesettings, file)

    settingsfile = os.path.join(launcherappdata, "settings.json")
    customdirectory = readsettings("customdirectory")
    if customdirectory:
        gamedirectory = customdirectory
    else:
        console.print("no custom directory found", style="muted")
    parentdirectory = os.path.dirname(os.path.normpath(gamedirectory))
    console.print("checking for pre-existing game install..", style="info")
    if os.path.isdir(gamedirectory):
        console.print("game install found!", style="success")
        console.print("checking if ac watchdog exists", style="info")
        if os.path.isfile(acwatchdogpath):
            console.print("found ac watchdog", style="success")
        else:
            console.print("failed to find ac watchdog", style="error")
            console.print("\n \n do you want to repair the game? \n not repairing will result in a non functional game.", style="question")
            consent = input("\n y/n? ").strip().lower()
            if consent in ("y", "yes"):
                console.print("continuing", style="info")
                if installgame(False):
                    clearconsole()
                    console.print("Meow.net installed!", style="success")
                    console.print("Going to menu!", style="info")
                    time.sleep(1)
                    return
        updatecheck()
        return
    else:
        console.print("\n \n game install not found, do you want to install? \n declining this will close the launcher.", style="question")
        consent = input("\n y/n? ").strip().lower()
        if consent in ("y", "yes"):
            console.print("continuing", style="info")
            if installgame(False):
                clearconsole()
                console.print("Meow.net installed!", style="success")
                console.print("Going to menu!", style="info")
                time.sleep(1)
                return
            else:
                clearconsole()
                console.print("install game failed, restart the launcher", style="error")

        else:
            sys.exit()


def repairgame():
    global parentdirectory
    console.print("Uninstalling Meow.Net...", style="info")
    parentdirectory = os.path.dirname(os.path.normpath(gamedirectory))
    shutil.rmtree(gamedirectory, ignore_errors=True)
    console.print("Uninstalled Meow.Net", style="success")
    console.print("Beginning installation", style="info")
    if installgame(True):
        console.print("Successfully repaired Meow.Net!", style="success")
        return
    else:
        console.print("Failed to repair Meow.Net!", style="error")
        time.sleep(3)
        return
    

def gameintegcheck():
    if os.path.isdir(os.path.join(gamedirectory, "BepInEx", "plugins")) & os.path.isfile(os.path.join(gamedirectory, "BepInEx", "plugins", "WoofPatch.dll")):
        return True
    else:
        return False



def launch_game():
    global watchdogpath
    clearconsole()
    console.print("checking game integrity", style="info")
    if gameintegcheck():
        console.print("passed integ check", style="success")
    else:
        console.print("Didn't pass integrity check. Do you want to repair Meow.Net? Not repairing will result in the game being in a broken state.", style="question")
        choice = input("y/n? ")
        if choice in ["yes", "y", ""]:
            clearconsole()
            repairgame()
    console.print("launching Meow.Net!", style="accent")
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
    watchdogprocess = subprocess.Popen(
        [acwatchdogpath],
        cwd=os.path.dirname(acwatchdogpath),
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    input("Press enter to close launcher..")
    sys.exit()



def showmenu():
    clearconsole()

    title = Group(
        Panel.fit(
            "[title]cay's meownet launcher[/]",
            border_style="title"
        ),
        "[accent]    made by @cayrr.s <3[/]",
    )

    options = Group(
        " ",
        "\n[accent]1. Launch Meow.Net[/]",
        f"\n[accent]2. Change Launch Mode current: [question]{launchmode}[/][/]",
        "\n[accent]3. Make desktop shortcut[/]",
        f"\n[accent]4. Change install location current: [question]{gamedirectory}[/][/]",
        "\n[accent]5. Repair Meow.Net[/]",
    )

    options = Padding(
        options,
        (0, 0, 0, 15)
    )

    console.print(Align.center(title))
    console.print(Align.center(options))




def main():
    global launchmode

    while True:
        showmenu()
        width = shutil.get_terminal_size().columns
        text = "Enter a choice: "
        print("\n")
        console.print(" " * ((width - len(text)) // 2), end="")
        choice = console.input("[prompt]Enter a choice:[/]")
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
            console.print("Made desktop shortcut!", style="success")
            time.sleep(1)
        if choice == "4":
            clearconsole()
            movegame()
        if choice == "5":
            clearconsole()
            repairgame()




atexit.register(reset_terminal_bg)
init()
main()