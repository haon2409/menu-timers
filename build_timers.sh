#!/bin/bash
cd ~/Projects/menu/menu_timers
pyinstaller --noconfirm --onedir --windowed \
  --icon=icon64.png \
  --add-data "alert.mp3:." \
  --add-data "icon64.png:." \
  --add-data "Info.plist:." \
  --name TimerApp \
  --osx-bundle-identifier com.yourcompany.timerapp \
  timers.py

# Sao chép Info.plist tùy chỉnh vào bundle
cp Info.plist dist/TimerApp.app/Contents/Info.plist