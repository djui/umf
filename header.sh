#!/bin/sh
tail +3 $0|unxz|tar x;python game.min.py;exit
