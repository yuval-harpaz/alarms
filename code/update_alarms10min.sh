#!/bin/bash
while true; do
    python code/alarms3.py
    git commit -a -m "10min update"
    git pull --no-edit
    git push
    python code/scrap_alarms.py
    current_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Current Time: $current_time"
    echo "going to sleep"
    sleep 600
done
