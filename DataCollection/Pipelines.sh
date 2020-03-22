#!/bin/sh 

while :
do
  echo "Press <CTRL+C> to exit."
  pgrep python3 | xargs kill -9
  sleep 2
  python3 Pipelines.py
  sleep 2
done
