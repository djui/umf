import curses
from math import sqrt
import pygame
from random import seed, shuffle, randint as ri
from itertools import product
import time

SCR = curses.initscr()
#curses.start_color()
SCR.keypad(1)

SCRH, SCRW = SCR.getmaxyx()

TILEW, TILEH = 5, 3

TBLOCK = 0
TGROUND = 1
TOUT = 2
TFLOWER = 3
TEND = 254
TPLAYER = 255

MAZEW, MAZEH = 20, 20
MAZE = [TBLOCK for x in range(MAZEW * MAZEH)]

SHADE = [' ', ' ', '.', ',', '+', curses.ACS_PLMINUS, '#', curses.ACS_CKBOARD, chr(178)]


def genmaze(s):
    global MAZE
    MAZE = [TBLOCK for x in range(MAZEW * MAZEH)]

    seed(s)

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

        #SCRH, SCRW = SCR.getmaxyx()
        #SCR.erase()
        #px, py = MAZEW // 2, MAZEH // 2
        #vw, vh = SCRW // TILEW, SCRH // TILEH
        #vx, vy = px - vw // 2, py - vh // 2
        #drawmaze(px, py, vx, vy, vw, vh)
        #SCR.move(SCRH - 1, SCRW - 1)
        #SCR.refresh()
        #time.sleep(0.01)

    while True:
        i = ri(0, MAZEW * MAZEH - 1)
        if MAZE[i] == TGROUND:
            MAZE[i] = TEND
            break

    i = MAZE.index(TGROUND)
    px, py = i % MAZEW, i / MAZEW

    i = MAZE.index(TEND)
    ex, ey = i % MAZEW, i / MAZEW
    for xy in path(px, py, ex, ey):
        i = xy[0] + xy[1] * MAZEW
        t = MAZE[i]
        if t == TGROUND:
            MAZE[i] = TFLOWER

    return px, py

class Node:
    def __init__(self, x, y, t):
        if t == TGROUND or t == TEND or t == TFLOWER:
            self.c = 0
        else:
            self.c = 1000
        self.p = None
        self.xy = (x, y)


def path(x0, y0, x1, y1):
    def h(xy, end):
        return sqrt((xy[0] - end[0]) ** 2 + (xy[1] - end[1]) ** 2)
    nodes = [[Node(x, y, MAZE[x + y * MAZEW]) for y in range(MAZEH)] for x in range(MAZEW)]
    graph = {}
    for x, y in product(range(MAZEW), range(MAZEH)):
        ns = []
        for i, j in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            if 0 <= x + i < MAZEW and 0 <= y + j < MAZEH:
                t = MAZE[x + y * MAZEW]
                if t == TGROUND or t == TEND or t == TFLOWER:
                    ns.append(nodes[x + i][y + j])
        graph[nodes[x][y]] = ns
    os = set()
    cs = set()
    end = nodes[x1][y1]
    c = nodes[x0][y0]
    os.add(c)
    while os:
        c = min(os, key=lambda n:n.c + h(n.xy, (x1, y1)))
        if c == end:
            p = []
            while c.p:
                p.append(c.xy)
                c = c.p
            p.append(c.xy)
            return p[::-1]
        os.remove(c)
        cs.add(c)
        for n in graph[c]:
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
        return SHADE[max(0, min(i, len(SHADE) - 1))]
    else:
        return ch


def drawtile(t, tx, ty, px, py, sx, sy):
    if t == TGROUND:
        ch = ' '
    elif t == TBLOCK:
        ch = curses.ACS_CKBOARD
    elif t == TOUT:
        ch = 'O'
    elif t == TEND:
        ch = 'V'
    elif t == TPLAYER:
        ch = curses.ACS_DIAMOND
    elif t == TFLOWER:
        ch = 'i'
    else:
        ch = '?'

    d = sqrt((px - tx) ** 2 + (py - ty) ** 2)
    df = 25.0 / max(1.0, d * d)

    #curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    for x in range(max(0, sx), min(SCRW, sx + TILEW)):
        for y in range(max(0, sy), min(SCRH, sy + TILEH)):
            #try:
            SCR.addch(y, x, shade(ch, df)) #, curses.color_pair(1))
            #except curses.error:
            #    pass


def drawmaze(px, py, vx, vy, vw, vh):
    for x, y in product(range(vx, vx + vw), range(vy, vy + vh)):
        drawtile(gettile(x, y), x, y, px, py, (x - vx) * TILEW, (y - vy) * TILEH)


def canmove(x, y):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        t = MAZE[x + y * MAZEW]
        return t == TGROUND or t == TEND or t == TFLOWER
    else:
        return False


def idx(x, y):
    return x + y * MAZEW


def gettile(x, y):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        return MAZE[x + y * MAZEW]
    else:
        return TOUT


def main():
    SCR.nodelay(1)

    # Music
    pygame.mixer.init(44100, -16, 2, 4096)
    pygame.mixer.music.load('music.xm')
    pygame.mixer.music.play()
    #sound = pygame.mixer.Sound('boom.wav')
    #time.sleep(2)
    #sound.play()


    level_seed = 1337
    px, py = genmaze(level_seed)
    old = gettile(px, py)

    playing = True

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

        if MAZE[idx(px, py)] == TEND:
            level_seed += 1
            px, py = genmaze(level_seed)

        old = MAZE[idx(px, py)]
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
