#!/usr/bin/bash
cd ~/alarms/code
python war23_idf2db.py
python war23_map2db.py
python war23_haa2db.py
python war23_db_tests.py
while test $# != 0
do
    case "$1" in
    -s) echo "stories" ; python war23_stories_update.py ;;
    -a) echo "not implemeted yet" ;;
    esac
    shift
done

