#!/bin/bash
while true; do
    python code/alarms3.py
    git commit -a -m "10min update"
    git pull --no-edit
    git push
    sleep 600
done
