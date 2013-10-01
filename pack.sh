#!/bin/sh

BIN=bin/play

mkdir -p bin

# Pack
./mnfy game.py > game.min.py
tar -cf - game.min.py music.xm die.xm | xz -9e -c > pack.txz

cat header.sh pack.txz > $BIN
chmod 0777 $BIN
