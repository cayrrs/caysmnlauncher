import psutil

blockingprocesses = ["cheatengine", "cheat engine", "ce.exe", "cheatengine-x86_64", # thanks github
        "artmoney", "tsearch", "punchii", "memhax", "scanmem",
        "xenos", "extremeinjector", "winject", "ginjector", "remoteinjector",
        "manninjector", "injectdll", "dllinjector", "processinjector",
        "speedhack", "gamespeed", "cheatengine-speedhack",
        "aimbot", "triggerbot", "wallhack", "esp_hack", "boneaimbot",
        "ollydbg", "x64dbg", "x32dbg", "windbg", "immunitydebugger",
        "wemod", "trainerfx", "plitch", "mrantifuncheat", "unknowncheats",
        "autohotkey", "autoit3", "xdotool",
        "antianticheat", "eacbypass", "battleye_bypass", "vacbypass",
        "be_bypass", "cerberus_bypass", "driver_bypass",
        "wpepro", "cheatburger", "packetsender",
        "hacker", "exploit", "bypass", "trainer",
        "godmode", "noclip", "spinbot", "rapidfire",
        "bunnyhop", "bhop", "fakelag",
        "hack.exe", "cheat.exe", "inject.exe", "loader.exe", "bypass.exe",
        "debugger", "ida.exe"]


def IsBlockingProcess(): # just writing bullshit
    processnames = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processnames.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    for name in processnames:
        if not name:
            continue

        process_name = name.lower()
        base_name = process_name[:-4] if process_name.endswith(".exe") else process_name

        for blocked in blockingprocesses:
            blocked_name = blocked.lower()
            blocked_base = blocked_name[:-4] if blocked_name.endswith(".exe") else blocked_name

        
            if base_name == blocked_base:
                return False, name

    
            if len(blocked_base) >= 6 and blocked_base in base_name:
                return False, name

    return True, None