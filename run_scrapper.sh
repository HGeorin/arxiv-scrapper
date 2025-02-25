#!/bin/bash
cd /home/user/hgeorin/code/arxiv-scrapper/cs-scrapper

while true
do
  python scrapper-main.py
  if [ $? -eq 0 ]; then
    echo "Scrapper ran successfully."
    break
  else
    echo "Scrapper crashed. Restarting..."
    sleep 5  # 等待5秒后重新启动
  fi
done