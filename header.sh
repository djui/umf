#!/bin/sh
tail -n +3 $0|unxz|tar x;python game.min.py;exit
