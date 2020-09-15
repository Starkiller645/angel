echo "AUTOMATED BATCH BUILD OF INSTALLER STARTED"
echo "[BUILD] Beginning build of Python files"
python build-cxfreeze.py build
echo "[BUILD] Done!"
echo "[PREPR] Preparing files in final locations"
cp .\Installer.nsi .\build\exe.win-amd64-3.8\Installer.nsi
echo "[PREPR] Copied installer script"
cp .\LICENSE .\build\exe.win-amd64-3.8\LICENSE.txt
echo "[PREPR] Copied LICENSE.txt"
cp .\angel\assets\* .\build\exe.win-amd64-3.8\
echo "[PREPR] Copied assets"
echo "[PREPR] Done!"
echo "[MOVNG] Moving files around"
cd .\build\exe.win-amd64-3.8\
echo "[MOVNG] Changing CWD"
mv .\__init__.exe .\Angel.exe
echo "[MOVNG] Moving executable file"
mv ".\reddit white.svg" .\redditwhite.svg
echo "[MOVNG] Done!"
echo "[BINST] Building installer file: this may take some time..."
makensis .\Installer.nsi
echo "[BINST] Done!"
echo "[MOVNG] Moving back to root directory"
cd ..\..\
echo "[MOVNG] Done!"
echo "[CPING] Copying installer to root directory"
cp .\build\exe.win-amd64-3.8\Installer.exe ".\Angel for Reddit Installer.exe"
echo "[CPING] Done!"
echo "[CLEAN] Cleaning up build files"
rm -r .\build\
rm .\__init__.spec
echo "[CLEAN] Done!"
echo "AUTOMATED BATCH BUILD FINISHED WITH STATUS 0"
