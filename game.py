import curses
from random import seed, randint as ri
from math import sqrt
import time

SCR = curses.initscr()
SCR.keypad(1)

SCRH, SCRW = SCR.getmaxyx()

TILEW, TILEH = 5, 3
MSIZE = 100
MAZE = [ri(0, 1) for x in range(MSIZE * MSIZE)]
SHADE = [' ', curses.ACS_BOARD, curses.ACS_CKBOARD]

VX, VY = 0, 0
PX, PY = 0, 0


def genmaze(s, w, h):
    seed(s)
    m, s = [0] * (w * h), [(ri(0, w), ri(0, h))]
    #while 1:
    #    p = s.pop(0)
    return m


def shade(b):
    return SHADE[b * len(SHADE) / 256]


def drawtile(t, tw, th, tx, ty, px, py, sx, sy):
    if t == 0:
        b = 0
    else:
        b = 255

    for x in range(max(0, sx), min(SCRW, sx + tw)):
        for y in range(max(0, sy), min(SCRH, sy + th)):
            try:
                d = 0.5 * sqrt((px - tx) * (px - tx) + (py - ty) * (py - ty))
                bb = min(255, max(0, b / int(max(1, d))))
                SCR.addch(1 + y, 1 + x, shade(bb))
            except curses.error:
                pass


def drawmaze(m, mw, mh, px, py, vx, vy, vw, vh):
    for x in range(max(0, vx), min(mw, vx + vw)):
        for y in range(max(0, vy), min(mh, vy + vh)):
            drawtile(m[x + y * mw], TILEW, TILEH, x, y, px, py, (x - vx) * TILEW, (y - vy) * TILEH)


def main():
    SCR.nodelay(1)

    playing = True

    vx, vy = 0, 0

    while playing:
        SCRH, SCRW = SCR.getmaxyx()

        SCR.erase()

        drawmaze(MAZE, MSIZE, MSIZE, 10, 10, vx, vy, SCRW - 1, SCRH - 1)

        ch = SCR.getch()
        if ch == curses.KEY_UP:
            vy -= 1
        elif ch == curses.KEY_DOWN:
            vy += 1
        elif ch == curses.KEY_LEFT:
            vx -= 1
        elif ch == curses.KEY_RIGHT:
            vx += 1
        elif ch == 27:
            playing = False

        SCR.move(SCRH - 1, SCRW - 1)
        SCR.refresh()
        time.sleep(0.01)

if __name__ == '__main__':
    try:
        main()
    finally:
        curses.endwin()
