#!/bin/bash
HOST=$1
USER=$2
PASSWORD=$3
SOURCE=$4

cd /Users/kapo/PycharmProjects/yolov5/$4
pwd

ftp -inv $HOST <<EOF
user $USER $PASSWORD

mget *

EOF