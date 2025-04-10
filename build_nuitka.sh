rm -rf output
yes | python -m nuitka --onefile --output-dir=output --macos-create-app-bundle --macos-app-mode=gui --macos-app-icon=resources/icon.icns main.py
mv output/Resources output/main.app/Contents/Resources
mv output/Info.plist output/main.app/Contents/Info.plist
mv output/main.app "output/Venti Server Manager.app"