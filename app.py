from tools.launchtokengenerator import writelaunchtoken
import os
import tools.defenderexclusion
import requests
import time
import sys
from zipfile import ZipFile
import shutil
import subprocess
from pyshortcuts import make_shortcut

# variables

localappdata = os.getenv('LOCALAPPDATA')
meownetappdata = os.path.join(localappdata, "MeowNet")
rootenv = os.getenv('SystemDrive')
root = os.path.join(rootenv, os.sep)
gamedirectory = os.path.join(root, "Meow.Net") # eventually i'll make this user changable, im too lazy rn icl
game_download_link = "https://cdn.cookedasset.com/build/Meow_Beta.zip" 
launchmode = "vr"
exepath = os.path.abspath(sys.argv[0])
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


def extractzip(zipfile):
    with ZipFile(zipfile, 'r') as zip:
        zip.extractall(root)


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



def installgame():
    clearconsole()
    print("creating temporary folder..")
    os.makedirs(os.path.join(root, "installer_temp"), exist_ok=True)
    print("downloading latest version of meow.net...")
    destpath = download_file(game_download_link, os.path.join(root, "installer_temp", "Meow_Beta.zip"))
    print("\n finished downloading meow.net")
    print("\n extracting Meow_Beta.zip... (this may take some time)")
    extractzip(destpath)
    if os.path.isdir(gamedirectory):
        print("extracted successfully!")
        print("cleaning up..")
        shutil.rmtree(os.path.join(root, "installer_temp"), ignore_errors=True)
        clearconsole()
        print("it is HIGHLY recommended that you add a defender exclusion for meownet. \n without one, the patch can be deleted by defender and you will have to reinstall to fix it. \n this CAN be reverted! search up how to remove windows defender exclusions")
        consent = input("\n add exclusion? y/n ").strip().lower()
        if consent in ("", "y", "yes"):
            tools.defenderexclusion.add_defender_exclusion(gamedirectory)
        return True
    else:
        return False
    
        



def init():
    print("creating required directories..")
    if os.path.isdir(meownetappdata):
        print("meownet app data found")
    else:
        print("meownet app data not found, making")
        os.mkdir(meownetappdata)
    print("checking for pre-existing game install..")
    if os.path.isdir(gamedirectory):
        print("game install found!")
        return
    else:
        print("\n \n game install not found, do you want to install? \n declining this will close the launcher.")
        consent = input("\n y/n? ").strip().lower()
        if consent in ("y", "yes"):
            print("continuing")
            if installgame():
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


def launch_game():
    clearconsole()
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
    print("\n\n\n\n\n\n")
    print("1. Launch Meow.Net")
    print(f"2. Change Launch Mode  current: {launchmode}")
    print(f"3. Make desktop shortcut")
    


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





init()
main()