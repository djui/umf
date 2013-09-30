#!/bin/sh
tail +3 $0>_.xz;unxz _.xz;tar xf _.tar;python game.min.py;exit
