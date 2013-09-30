#!/bin/sh

SRC=game.py
BIN=bin/play

# Pack
mkdir -p bin
xz -9e --keep --force $SRC
cat header.sh $SRC.xz > $BIN
chmod 0777 $BIN

# Just for comparison
python -m compileall . > /dev/null
./mnfy $SRC > $(basename $SRC .py).min.py
