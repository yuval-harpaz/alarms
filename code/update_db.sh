#!/usr/bin/bash
cd ~/alarms/code
python war23_idf2db.py
python scrap.py
python war23_db_tools.py --db2map
python scrap.py
python war23_haa2db.py
python scrap.py
python war23_db_front.py
python scrap.py
python war23_front2db.py
python scrap.py
while test $# != 0
do
    case "$1" in
    -s) echo "stories" ; python war23_stories_update.py ;;
    -b) python war23_btl_new.py ;;
    -a) echo "not implemented yet" ;;
    esac
    shift
done
python scrap.py
python war23_db_tests.py
python scrap.py

