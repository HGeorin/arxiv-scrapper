#!/bin/bash

while true; do
    echo "starting download..."
    pkill -f scrapper-main.py
    python /home/user/hgeorin/code/arxiv-scrapper/cs-scrapper/downloader.py &
    sleep 1h  # 每 1 小时重启一次
done
