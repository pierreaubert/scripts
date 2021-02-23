#!/bin/bash
tbk=$(ps aux | grep Roon |  grep -v grep| awk '{print $2}')
for p in $tbk ; do
    kill -9 $p;
done
nohup ./RoonServer/start.sh > nohup-roon.out