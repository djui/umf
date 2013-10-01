import curses
from math import sqrt
import pygame
from random import seed, shuffle, randint as ri, random
import time

SCR = curses.initscr()
#curses.start_color()
SCR.keypad(1)

SCRH, SCRW = SCR.getmaxyx()

TILEW, TILEH = 5, 3

TBLOCK = 0
TGROUND = 1
TOUT = 2
TPLAYER = 255
TEND = 254

MAZEW, MAZEH = 20, 20
MAZE = [TBLOCK for x in range(MAZEW * MAZEH)]

SHADE = [' ', ' ', '.', ',', '+', curses.ACS_PLMINUS, '#', curses.ACS_CKBOARD, ' ']


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


class Node:
    def __init__(self, xy):
        self.c = 0
        self.p = None
        self.xy = xy


def vadd(xy, dxy):
    return (xy[0] + dxy[0], xy[1] + dxy[1])


def path(x0, y0, x1, y1):
    openset = set()
    closedset = set()
    current = Node((x0, y0))
    openset.add(current)
    while openset:
        current = min(openset, key=lambda n:n.c)
        if current.xy == end.xy:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
        openset.remove(current)
        closedset.add(current)
        for move in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            node = Node(vadd(current.xy, move))
            if node in closedset:
                continue
            if node in openset:
                new_c = current.c + 1
                if node.c > new_c:
                    node.c = new_c
                    node.parent = current
            else:
                node.c = current.c + 1
                node.parent = current
                openset.add(node)
    return None


def shade(ch, b):
    if ch in SHADE:
        i = int(b * float(SHADE.index(ch)))
        if i > 7:
            return (' ', curses.A_REVERSE)
        return (SHADE[max(0, min(i, len(SHADE) - 1))], 0)
    else:
        return (ch, 0)


def drawtile(t, tx, ty, px, py, sx, sy):
    if t == TGROUND:
        ch = ' '
    elif t == TBLOCK:
        ch = curses.ACS_CKBOARD
    elif t == TOUT:
        ch = curses.ACS_CKBOARD
    elif t == TEND:
        SCR.addstr(sy,   sx, '    _')
        SCR.addstr(sy+1, sx, '  _|#')
        SCR.addstr(sy+2, sx, '_|###')
        return
    elif t == TPLAYER:
        SCR.addstr(sy,   sx, '  o /')
        SCR.addstr(sy+1, sx, '()|` ')
        SCR.addstr(sy+2, sx, ' / \ ')
        return
    else:
        ch = '?'

    d = sqrt((px - tx) ** 2 + (py - ty) ** 2)
    df = 15.0 / max(1.0, d * d) + random()/20 # Flickering


    #curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    for x in range(max(0, sx), min(SCRW, sx + TILEW)):
        for y in range(max(0, sy), min(SCRH, sy + TILEH)):
            #try:
            (sch, attr) = shade(ch, df)
            SCR.addch(y, x, sch, attr) #, curses.color_pair(1))
            #except curses.error:
            #    pass


def drawmaze(px, py, vx, vy, vw, vh):
    for x in range(vx, vx + vw):
        for y in range(vy, vy + vh):
            drawtile(gettile(x, y), x, y, px, py, (x - vx) * TILEW, (y - vy) * TILEH)


def canmove(x, y):
    if 0 <= x < MAZEW and 0 <= y < MAZEH:
        t = MAZE[x + y * MAZEW]
        return t == TGROUND or t == TEND
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

    level_seed = 1337

    genmaze(level_seed)

    # Music
    pygame.mixer.init(44100, -16, 2, 4096)
    #pygame.mixer.music.load('music.xm')
    #pygame.mixer.music.play()
    #sound = pygame.mixer.Sound('boom.wav')
    #time.sleep(2)
    #sound.play()

    old = TGROUND
    i = MAZE.index(TGROUND)
    px, py = i % MAZEW, i / MAZEW

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
            genmaze(level_seed)
            i = MAZE.index(TGROUND)
            px, py = i % MAZEW, i / MAZEW

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
