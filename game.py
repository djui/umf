import curses
from math import sqrt
import pygame
from random import seed, shuffle, randint as ri
import time

SCR = curses.initscr()
SCR.keypad(1)

SCRH, SCRW = SCR.getmaxyx()

TILEW, TILEH = 5, 3

TBLOCK = 0
TGROUND = 1
TOUT = 2
TPLAYER = 255

MAZEW, MAZEH = 100, 100
MAZE = [TBLOCK for x in range(MAZEW * MAZEH)]

SHADE = [' ', ' ', '.', ',', '+', curses.ACS_PLMINUS, '#', curses.ACS_CKBOARD, chr(178)]


def genmaze(s):
    seed(s)
    SCRH, SCRW = SCR.getmaxyx()
    n = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    m, w, h = MAZE, MAZEW, MAZEH
    v, s = [], []
    x0, y0 = (1 + ri(0, (w - 1) // 2) * 2, 1 + ri(0, (h - 1) // 2) * 2)
    while len(v) < len(m):
        v.append((x0, y0))
        m[x0 + y0 * w] = TGROUND
        found = False
        shuffle(n)
        for d in n:
            x1, y1 = x0 + d[0], y0 + d[1]
            if 0 <= x1 < w and 0 <= y1 < h:
                if (x1, y1) not in v:
                    m[x1 + y1 * w] = TGROUND
                    #if gettile(x1 - 1, y1 + 1) or gettile(x1 - 1, y1 - 1):
                    #    v.append((x1 - 1, y1))
                    #if gettile(x1 + 1, y1 + 1) or gettile(x1 + 1, y1 - 1):
                    #    v.append((x1 + 1, y1))
                    #if gettile(x1 - 1, y1 - 1) or gettile(x1 + 1, y1 - 1):
                    #    v.append((x1, y1 - 1))
                    #if gettile(x1 - 1, y1 + 1) or gettile(x1 + 1, y1 + 1):
                    #    v.append((x1, y1 + 1))
                    v.append((x0, y0))
                    s.append((x0, y0))
                    x0, y0 = x1, y1
                    found = True
                    break
        if not found:
            if len(s) > 0:
                x0, y0 = s.pop()
            else:
                break

        #SCR.erase()
        #px, py = MAZEW // 2, MAZEH // 2
        #vw, vh = SCRW // TILEW, SCRH // TILEH
        #vx, vy = px - vw // 2, py - vh // 2
        #drawmaze(px, py, vx, vy, vw, vh)
        #SCR.move(SCRH - 1, SCRW - 1)
        #SCR.refresh()
        #time.sleep(0.01)


def path(x0, y0, x1, y1):
    return x0, y0


def shade(ch, b):
    if ch in SHADE:
        i = int(b * float(SHADE.index(ch)))
        return SHADE[max(0, min(i, len(SHADE) - 1))]
    else:
        return ch


def drawtile(t, tx, ty, px, py, sx, sy):
    if t == TGROUND:
        ch = ' '
    elif t == TBLOCK:
        ch = curses.ACS_CKBOARD
    elif t == TOUT:
        ch = '@'
    elif t == TPLAYER:
        ch = curses.ACS_DIAMOND
    else:
        ch = '?'

    d = sqrt((px - tx) * (px - tx) + (py - ty) * (py - ty))
    df = 25.0 / max(1.0, d * d)

    for x in range(max(0, sx), min(SCRW, sx + TILEW)):
        for y in range(max(0, sy), min(SCRH, sy + TILEH)):
            #try:
            SCR.addch(y, x, shade(ch, df))
            #except curses.error:
            #    pass


def drawmaze(px, py, vx, vy, vw, vh):
    for x in range(vx, vx + vw):
        for y in range(vy, vy + vh):
            drawtile(gettile(x, y), x, y, px, py, (x - vx) * TILEW, (y - vy) * TILEH)


def canmove(x, y):
    return 0 <= x < MAZEW and 0 <= y < MAZEH and MAZE[x + y * MAZEW] == TGROUND


def idx(x, y):
    return x + y * MAZEW


def gettile(x, y):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        return MAZE[x + y * MAZEW]
    else:
        return TOUT


def main():
    SCR.nodelay(1)

    genmaze(1337)

    playing = True

    # Music
    pygame.mixer.init(44100, -16, 2, 4096)
    pygame.mixer.music.load('music.xm')
    pygame.mixer.music.play()
    #sound = pygame.mixer.Sound('boom.wav')
    #time.sleep(2)
    #sound.play()

    old = TGROUND
    i = MAZE.index(TGROUND)
    px, py = i % MAZEW, i / MAZEW

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
        elif ch == 32:
            curses.flash()
        elif ch == 27:
            playing = False

        MAZE[idx(px, py)] = TPLAYER

        # ai

        SCR.addstr(1, 2, str(int(ch)))
        SCR.addstr(2, 2, str(px) + ',' + str(py))

        SCR.move(SCRH - 1, SCRW - 1)
        SCR.refresh()
        time.sleep(0.01)

if __name__ == '__main__':
    #try:
        main()
    #finally:
    #    curses.nocbreak()
    #    SCR.keypad(0)
    #    curses.echo()
    #    curses.endwin()
