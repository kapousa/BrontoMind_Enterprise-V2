#! /bin/bash
SRC=$1
NAM=$2
cd /
cd /Users/kapo/PycharmProjects/yolov5
source venv/bin/activate

python3 detect.py --source $SRC --name $NAM
