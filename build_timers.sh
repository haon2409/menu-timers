#!/bin/bash
cd ~/Projects/menu/menu_timers
pyinstaller --noconfirm --onedir --windowed \
  --icon=icon64.png \
  --add-data "alert.mp3:." \
  --add-data "icon64.png:." \
  --name TimerApp \
  --osx-bundle-identifier com.yourcompany.timerapp \
  timers.py