#!/bin/bash
while true; do
    python code/alarms3.py
    git commit -a -m "10min update"
    git pull --no-edit
    git push
    python code/scrap_alarms.py
    sleep 600
done
