import curses
from random import seed, randint as ri
from math import sqrt
import time

SCR = curses.initscr()
SCR.keypad(1)

SCRH, SCRW = SCR.getmaxyx()

TILEW, TILEH = 5, 3
MAZEW, MAZEH = 100, 100
MAZE = [ri(0, 1) for x in range(MAZEW * MAZEH)]
SHADE = [' ', '.', ',', '+', curses.ACS_PLMINUS, '#', curses.ACS_CKBOARD, chr(178)]
PTILE = 255


def genmaze(s, w, h):
    seed(s)
    m, s = [0] * (w * h), [(ri(0, w), ri(0, h))]
    #while 1:
    #    p = s.pop(0)
    return m


def shade(ch, b):
    if ch in SHADE:
        i = int(b * float(SHADE.index(ch)))
        return SHADE[max(0, min(i, len(SHADE) - 1))]
    else:
        return ch


def drawtile(t, tx, ty, px, py, sx, sy):
    if t == 0:
        ch = ' '
    elif t == 1:
        ch = curses.ACS_CKBOARD
    elif t == 255:
        ch = curses.ACS_DIAMOND

    d = sqrt((px - tx) * (px - tx) + (py - ty) * (py - ty))
    df = 5.0 / max(1.0, d)

    for x in range(max(0, sx), min(SCRW, sx + TILEW)):
        for y in range(max(0, sy), min(SCRH, sy + TILEH)):
            try:
                SCR.addch(1 + y, 1 + x, shade(ch, df))
            except curses.error:
                pass


def drawmaze(px, py, vx, vy, vw, vh):
    for x in range(max(0, vx), min(MAZEW, vx + vw)):
        for y in range(max(0, vy), min(MAZEH, vy + vh)):
            drawtile(MAZE[x + y * MAZEW], x, y, px, py, (x - vx) * TILEW, (y - vy) * TILEH)


def canmove(x, y):
    return 0 <= x < MAZEW and 0 <= y < MAZEH and MAZE[x + y * MAZEW] == 0


def idx(x, y):
    return x + y * MAZEW


def main():
    SCR.nodelay(1)

    playing = True

    old = 0
    px, py = 10, 10

    while playing:
        SCRH, SCRW = SCR.getmaxyx()

        SCR.erase()

        vw, vh = SCRW // TILEW, SCRH // TILEH
        vx, vy = px - vw // 2, py - vh // 2
        drawmaze(px, py, vx, vy, vw, vh)

        MAZE[idx(px, py)] = old

        ch = SCR.getch()
        if ch == curses.KEY_UP and canmove(px, py - 1):
            py -= 1
        elif ch == curses.KEY_DOWN and canmove(px, py + 1):
            py += 1
        elif ch == curses.KEY_LEFT and canmove(px - 1, py):
            px -= 1
        elif ch == curses.KEY_RIGHT and canmove(px + 1, py):
            px += 1
        elif ch == 27:
            playing = False

        MAZE[idx(px, py)] = PTILE

        # ai

        SCR.addstr(1, 2, str(int(ch)))
        SCR.addstr(2, 2, str(px) + ',' + str(py))

        SCR.move(SCRH - 1, SCRW - 1)
        SCR.refresh()
        time.sleep(0.01)

if __name__ == '__main__':
    try:
        main()
    finally:
        curses.endwin()
