#!/bin/bash
case $1 in
    "-h") echo 'Used: ./restart.sh (manage|monitor|all|-h|--help)'
    ;;
    "--help") echo 'Used: ./restart.sh (manage|monitor|all|-h|--help)'
    ;;
    *)  ./stop.sh $1
        ./start.sh $1
    ;;
esac

