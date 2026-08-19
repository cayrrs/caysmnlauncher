@echo off
setlocal

set /p VERSION=<version.txt
echo building the launcher... version %VERSION%

python -m nuitka --standalone --windows-console-mode=force --include-package=tools --output-filename=cayymnlauncher.exe --windows-icon-from-ico=mn.ico --company-name="cayy" --product-name="cay's mn launcher" --file-version=%VERSION% --product-version=%VERSION% --file-description="cay's mn launcher" --include-data-files=version.txt=version.txt --enable-plugin=tk-inter --assume-yes-for-downloads app.py

if %errorlevel% neq 0 (
    echo build failed!
    pause
    exit /b 1
)

echo build succeeded, zipping...

if exist cayymnlauncher.zip del cayymnlauncher.zip
powershell -Command "Compress-Archive -Path 'app.dist\*' -DestinationPath 'cayymnlauncher.zip'"

echo zip done, building installer...

where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo iscc not found on PATH, skipping installer build.
    echo install Inno Setup from https://jrsoftware.org/isinfo.php and add it to PATH.
    goto :done
)

iscc /DMyAppVersion="%VERSION%" installer.iss
if %errorlevel% neq 0 (
    echo installer build failed!
    pause
    exit /b 1
)

echo installer built: cayymnlauncher-setup.exe

:done
echo done! outputs: cayymnlauncher.zip, cayymnlauncher-setup.exe
pause