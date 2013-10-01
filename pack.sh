#!/bin/sh

BIN=bin/play

mkdir -p bin

# Pack
./mnfy game.py > _
tar -cf - _ music.xm | xz -9e -c > pack.txz

cat header.sh pack.txz > $BIN
chmod 0777 $BIN
