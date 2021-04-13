#!/bin/bash
case $1 in
    "manage")  ps -ef|grep manage.py|grep -v grep|awk '{print $2}'|xargs kill
    ;;
    "monitor")  ps -ef|grep monitor.py|grep -v grep|awk '{print $2}'|xargs kill
    ;;
    "-h") echo 'Used: ./stop.sh (manage|monitor|all|-h|--help)'
    ;;
    "--help") echo 'Used: ./stop.sh (manage|monitor|all|-h|--help)'
    ;;
    *)  ps -ef|grep manage.py|grep -v grep|awk '{print $2}'|xargs kill
        ps -ef|grep monitor.py|grep -v grep|awk '{print $2}'|xargs kill
    ;;
esac
