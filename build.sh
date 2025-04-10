rm -rf "dist/Venti Server Manager.app"
yes | pyinstaller --windowed --noconsole --icon=resources/icon.icns main.py
mv dist/main.app "dist/Venti Server Manager.app"