import time
from helios import Helios
from helios.helpers import make_point, color_shift_frame
import math

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

if numDevices is 0:
    print('Quitting (No Devices found)')
    exit()
Helios.SetShutter(0, 1)


def parse_hex_color(str, normalize=False):
    '''
    normalize: return color values between 0 and 1 (instead of 0 and 255)
    '''
    str = str.lstrip('#')
    if normalize:
        t = tuple( int(str[i:i+2], 16) / 255 for i in (0, 2, 4) )
    else:
        t = tuple( int(str[i:i+2], 16) for i in (0, 2, 4) )
    return (*t, 1)

def pattern_circle(scale=1, color=(1,1,1,1), n_points=100):
    p = []
    for i in range(n_points):
        a = 2 * math.pi / n_points * i
        p.append( make_point(scale * math.cos(a), scale * math.sin(a), *color) )
    return Helios.Frame(*p)


def pattern_square(scale=1, color=(1,1,1,1), n_points=100):
    t = []
    r = []
    b = []
    l = []
    n_fourth = int(n_points/4)
    for i in range(n_fourth):
        a = i / (n_fourth - 1) * 2 - 1 # [-1, 1]
        t.append( make_point(scale * a, -scale, *color) )
        r.append( make_point(scale, scale * a, *color) )
        b.append( make_point(scale * -a, scale, *color) )
        l.append( make_point(-scale, scale * -a, *color) )
    return Helios.Frame(*t, *r, *b, *l)


def pattern_x(scale=1, color=(1,1,1,1), n_points=100):
    total = 2 + math.sqrt(2) * 2
    side = int(n_points / total)
    diag = math.ceil(n_points / total * math.sqrt(2))
    
    tl_br = []
    b = []
    bl_tr = []
    t = []
    
    for i in range(diag):
        a = i / (diag-1) * 2 - 1 # [-1, 1]
        tl_br.append( make_point(scale * a, scale * a, *color) )
        bl_tr.append( make_point(scale * a, scale * -a, *color) )
    
    for i in range(side):
        a = i / (side-1) * 2 - 1 # [-1, 1]
        b.append( make_point(scale * -a, scale, 0,0,0,0) )
        t.append( make_point(scale * -a, -scale, 0,0,0,0) )
    
    return Helios.Frame(*tl_br, *b, *bl_tr, *t)


def pattern_color_hex(scale=1, n_points=100, colors=None):
    if colors is None:
        colors = [
            (1,0,0,1), # red
            (1,1,0,1), # yellow
            (0,1,0,1), # green
            (0,1,1,1), # cyan
            (0,0,1,1), # blue
            (1,0,1,1), # magenta
        ]
    t = 2 * math.pi / 6
    sixth = int(n_points / 6)
    out = []
    for i in range(6):
        a = t * i # start angle
        b = a + t # end angle
        c = colors[i] # color
        p1 = (scale * math.cos(a), scale * math.sin(a))
        p2 = (scale * math.cos(b), scale * math.sin(b))
        for i in range(sixth):
            a = i / (sixth-1)
            p = ( p1[0] + (p2[0]-p1[0])*a, p1[1] + (p2[1]-p1[1])*a )
            out.append( make_point(p[0], p[1], *c) )
    
    return Helios.Frame(*out)

colors = {
  "r": "#ff6868",
  "y": "#ffd770",
  "g": "#70ff94",
  "c": "#70c5ff",
  "b": "#566bef",
  "m": "#ee2f95",
}
colors = list(map(lambda x: parse_hex_color(x, True), colors.values(), ))



if __name__ == '__main__':
    PPS = 20000
    POINTS = 300
    SCALE = 0.3
    COLOR_SHIFT = 3

    patterns = [
        pattern_color_hex(SCALE, n_points=POINTS),
        pattern_color_hex(SCALE, n_points=POINTS, colors=colors),
        pattern_circle(SCALE, n_points=POINTS),
        pattern_square(SCALE, n_points=POINTS),
        pattern_x(SCALE, n_points=POINTS)
    ]

    try:
        current = 0
        print('press enter to switch patterns. press Ctrl-C to exit.')
        while True:
            pattern = patterns[current]
            pattern = color_shift_frame(pattern, COLOR_SHIFT)
            while Helios.GetStatus(0) != 1: time.sleep(1/1000) # wait 1 ms
            Helios.WriteFrame(0, PPS, Helios.FLAGS_DEFAULT, pattern, len(pattern))
            input()
            current += 1
            current = current % len(patterns)
    except KeyboardInterrupt:
        Helios.SetShutter(0, 0)
        Helios.CloseDevices()
        exit()
