#!/bin/bash
source ./venv/bin/activate
################################################
case $1 in
    "manage")  nohup python3 ./manage.py runserver --threaded 2>&1 &
    ;;
    "monitor")  python3 ./monitor.py 2>&1 &
    ;;
    "-h") echo 'Used: ./start.sh (manage|monitor|all|-h|--help)'
    ;;
    "--help") echo 'Used: ./start.sh (manage|monitor|all|-h|--help)'
    ;;
    *)  nohup python3 ./manage.py runserver --threaded 2>&1 &
        python3 ./monitor.py 2>&1 &
    ;;
esac
