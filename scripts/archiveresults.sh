#!/bin/bash
RUNID=$1
cd /Users/kapo/PycharmProjects/yolov5/runs/detect
cd $RUNID
zip -r $RUNID ./*
mv $RUNID.zip /Users/kapo/PycharmProjects/BrontoMind_Enterprise/app/detection
rm $RUNID.zip
