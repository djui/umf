#!/bin/sh

SRC=game.py
BIN=play.sh

xz -9e --keep --force $SRC
cat header.sh $SRC.xz > $BIN
chmod 0777 $BIN
