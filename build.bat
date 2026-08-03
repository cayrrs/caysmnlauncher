@echo off
echo building the launcher...

python -m nuitka --standalone --windows-console-mode=force --include-package=tools --output-filename=cayymnlauncher.exe --windows-icon-from-ico=mn.ico --company-name="cayy" --product-name="cay's mn launcher" --file-version=1.0.0.0 --product-version=1.0.0.0 --file-description="cay's mn launcher" --enable-plugin=tk-inter app.py

if %errorlevel% neq 0 (
    echo build failed!
    pause
    exit /b 1
)

echo build succeeded, zipping...

if exist cayymnlauncher.zip del cayymnlauncher.zip
powershell -Command "Compress-Archive -Path 'app.dist\*' -DestinationPath 'cayymnlauncher.zip'"

echo done! output: cayymnlauncher.zip
pause