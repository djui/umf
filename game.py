import curses
from math import sqrt
import pygame
from random import seed, shuffle, randint as ri, random
from itertools import product
import time

SCR = curses.initscr()
#curses.start_color()
SCR.keypad(1)

SCRH, SCRW = SCR.getmaxyx()

TILEW, TILEH = 5, 3

TBLOCK = 0
TGND = 1
TGND2 = 2
TOUT = 3
TFLW = 4
TEND = 5
TBAD = 254
TPLY = 255
WALK = [TGND, TGND2, TFLW, TEND]

MSPD = .35

MAZEW, MAZEH = 50, 50
MAZE = [TBLOCK for x in range(MAZEW * MAZEH)]

SHADE = [' ', ' ', '.', ',', '+', curses.ACS_PLMINUS, '#', curses.ACS_CKBOARD, ' ']


def genm(s):
    global MAZE
    MAZE = [TBLOCK for x in range(MAZEW * MAZEH)]

    seed(s)

    n = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    m, w, h = MAZE, MAZEW, MAZEH
    v, s = [], []
    x0, y0 = (1 + ri(0, (w - 1) // 2) * 2, 1 + ri(0, (h - 1) // 2) * 2)
    while len(v) < len(m):
        v.append((x0, y0))
        found = False
        shuffle(n)
        for d in n:
            x1, y1 = x0 + d[0], y0 + d[1]
            if 0 <= x1 < w and 0 <= y1 < h:
                if (x1, y1) not in v:
                    r = ri(0, 200)
                    if r < 2:
                        t = TFLW
                    elif r < 50:
                        t = TGND2
                    else:
                        t = TGND
                    m[x1 + y1 * w] = t
                    #if gett(x1 - 1, y1 + 1) or gett(x1 - 1, y1 - 1):
                    #    v.append((x1 - 1, y1))
                    #if gett(x1 + 1, y1 + 1) or gett(x1 + 1, y1 - 1):
                    #    v.append((x1 + 1, y1))
                    #if gett(x1 - 1, y1 - 1) or gett(x1 + 1, y1 - 1):
                    #    v.append((x1, y1 - 1))
                    #if gett(x1 - 1, y1 + 1) or gett(x1 + 1, y1 + 1):
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

        #SCRH, SCRW = SCR.getmaxyx()
        #SCR.erase()
        #px, py = MAZEW // 2, MAZEH // 2
        #vw, vh = SCRW // TILEW, SCRH // TILEH
        #vx, vy = px - vw // 2, py - vh // 2
        #drawm(px, py, vx, vy, vw, vh)
        #SCR.move(SCRH - 1, SCRW - 1)
        #SCR.refresh()
        #time.sleep(0.01)

    while True:
        i = ri(0, MAZEW * MAZEH - 1)
        if MAZE[i] in WALK:
            MAZE[i] = TEND
            break

    i = MAZE.index(TGND)
    px, py = i % MAZEW, i / MAZEW

    i = len(MAZE) - 1 - list(reversed(MAZE)).index(TGND)
    mx, my = i % MAZEW, i / MAZEW

    #i = MAZE.index(TEND)
    #ex, ey = i % MAZEW, i / MAZEW
    #for xy in path(px, py, ex, ey):
    #    i = xy[0] + xy[1] * MAZEW
    #    t = MAZE[i]
    #    if t == TGND:
    #        MAZE[i] = TFLW

    return px, py, mx, my


class Node:
    def __init__(self, x, y, t):
        if t in WALK:
            self.c = 0
        else:
            self.c = 1000
        self.p = None
        self.xy = (x, y)


def path(x0, y0, x1, y1):
    def h(xy, end):
        return sqrt((xy[0] - end[0]) ** 2 + (xy[1] - end[1]) ** 2)
    ns = [[Node(x, y, MAZE[x + y * MAZEW]) for y in range(MAZEH)] for x in range(MAZEW)]
    g = {}
    for x, y in product(range(MAZEW), range(MAZEH)):
        n = []
        for i, j in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            if 0 <= x + i < MAZEW and 0 <= y + j < MAZEH:
                t = MAZE[x + y * MAZEW]
                if t in WALK:
                    n.append(ns[x + i][y + j])
        g[ns[x][y]] = n
    os, cs = set(), set()
    c, end = ns[x0][y0], ns[x1][y1]
    os.add(c)
    while os:
        c = min(os, key=lambda n: n.c + h(n.xy, (x1, y1)))
        if c == end:
            p = []
            while c.p:
                p.append(c.xy)
                c = c.p
            p.append(c.xy)
            return p[::-1]
        os.remove(c)
        cs.add(c)
        for n in g[c]:
            if n in cs:
                continue
            if n in os:
                new_c = c.c + 1
                if n.c > new_c:
                    n.c = new_c
                    n.p = c
            else:
                n.c = c.c + 1
                n.p = c
                os.add(n)
    return None


def shade(ch, b):
    if ch in SHADE:
        i = int(b * float(SHADE.index(ch)))
        if i > 7:
            return (' ', curses.A_REVERSE)
        return (SHADE[max(0, min(i, len(SHADE) - 1))], 0)
    else:
        return (ch, 0)


def drawt(t, tx, ty, px, py, sx, sy):
    d = sqrt((px - tx) ** 2 + (py - ty) ** 2)

    if t == TGND:
        ch = ' '
    elif t == TGND2:
        SCR.addstr(sy,   sx, '.  ..')
        SCR.addstr(sy+1, sx, '  .  ')
        SCR.addstr(sy+2, sx, ' . ..')
        return
    elif t == TBLOCK or t == TOUT:
        ch = curses.ACS_CKBOARD
    elif t == TEND:
        SCR.addstr(sy,   sx, '    _')
        SCR.addstr(sy+1, sx, '  _|#')
        SCR.addstr(sy+2, sx, '_|###')
        return
    elif t == TPLY:
        SCR.addstr(sy,   sx, '  o /')
        SCR.addstr(sy+1, sx, '()|` ')
        SCR.addstr(sy+2, sx, ' / \ ')
        return
    elif t == TBAD:
        if d <= 4.:
            SCR.addstr(sy,   sx, ' _.. ')
            SCR.addstr(sy+1, sx, '(o O)')
            SCR.addstr(sy+2, sx, '/v^v\\')
        elif d <= 5.5:
            SCR.addstr(sy,   sx, '     ')
            SCR.addstr(sy+1, sx, ' o O ')
            SCR.addstr(sy+2, sx, ' , v ')
        elif d <= 7.:
            SCR.addstr(sy,   sx, '     ')
            SCR.addstr(sy+1, sx, ' . o ')
            SCR.addstr(sy+2, sx, '   , ')
        return
    elif t == TFLW:
        SCR.addstr(sy,   sx, '     ')
        SCR.addstr(sy+1, sx, '  w  ')
        SCR.addstr(sy+2, sx, '_\|/_')
        return
    else:
        ch = '?'

    df = 15.0 / max(1.0, d * d) + random()/20 # Flickering

    for x, y in product(range(sx, sx + TILEW), range(sy, sy + TILEH)):
        SCR.addch(y, x, *shade(ch, df))


def drawm(px, py, vx, vy, vw, vh):
    for x, y in product(range(vx, vx + vw), range(vy, vy + vh)):
        drawt(gett(x, y), x, y, px, py, (x - vx) * TILEW, (y - vy) * TILEH)


def canmove(x, y):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        t = MAZE[x + y * MAZEW]
        return t in WALK or t == TPLY or t == TBAD
    else:
        return False


def gett(x, y):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        return MAZE[x + y * MAZEW]
    else:
        return TOUT


def sett(x, y, t):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        MAZE[x + y * MAZEW] = t


def main():
    SCR.nodelay(1)

    # Music
    pygame.mixer.init(44100, -16, 2, 4096)
    sound = pygame.mixer.Sound('/usr/share/aisleroit/sounds/splat.ogg')
    sound2 = pygame.mixer.Sound('splat.ogg')
    #pygame.mixer.music.load('music.xm')
    #pygame.mixer.music.play()
    
    lvl = 1337
    px, py, mx, my = genm(lvl)

    pold, mold = gett(px, py), gett(mx, my)

    ms = MSPD

    st = time.time()

    playing = True

    while playing:
        now = time.time()
        ft, st = now - st, now

        SCRH, SCRW = SCR.getmaxyx()

        SCR.erase()

        vw, vh = SCRW // TILEW, SCRH // TILEH
        vx, vy = px - vw // 2, py - vh // 2
        drawm(px, py, vx, vy, vw, vh)

        sett(mx, my, mold)
        ms -= ft
        if ms < 0:
            ms = MSPD
            ps = path(mx, my, px, py)
            if ps and len(ps) > 1:
                mxx, myy = ps[1]
                if canmove(mxx, myy):
                    mx, my = mxx, myy
        mold = gett(mx, my)
        sett(mx, my, TBAD)

        sett(px, py, pold)
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

        t = gett(px, py)
        if t == TEND:
            lvl += 1
            px, py, mx, my = genm(lvl)
        elif (mx, my) == (px, py): # Caught!
            sound.play()
            sound2.play()
            curses.flash()
            px, py, mx, my = genm(lvl)
            mold, pold = TGND, TGND
            sett(mx, my, TBAD)
            sett(px, py, TPLY)
        else:
            pold = t
            sett(px, py, TPLY)

        #SCR.move(SCRH - 1, SCRW - 1)
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
