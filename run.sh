#!/bin/bash
pkill -f timers.py  # Dừng ứng dụng đang chạy
watchexec -e py -r -- python3 timers.py  # Theo dõi thay đổi và tự chạy lại
