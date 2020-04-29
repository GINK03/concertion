#!/bin/sh 

while :
do
  echo "Press <CTRL+C> to exit."
  pgrep python3 | xargs kill -9
  pgrep chrome | xargs kill -9
  sleep 2
  timeout 3600 python3 Pipelines.py
  sleep 2
done
