#!/usr/bin/bash
cd ~/alarms/code
python war23_idf2db.py
python war23_map2db.py
python war23_haa2db.py
python war23_db_tests.py

