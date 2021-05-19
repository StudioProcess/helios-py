import time
from helios import Helios
from helios.helpers import make_point, color_shift_frame
import math

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

if numDevices == 0:
    print('Quitting (No Devices found)')
    exit()
Helios.SetShutter(0, 1)


def pattern_circle(scale=1, n_points=100, color=(1,1,1,1),):
    p = []
    for i in range(n_points):
        a = 2 * math.pi / n_points * i
        p.append( make_point(scale * math.cos(a), scale * math.sin(a), *color) )
    return Helios.Frame(*p)


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

# 
# def pattern_square(scale=1, color=(1,1,1,1), n_points=100):
#     t = []
#     r = []
#     b = []
#     l = []
#     n_fourth = int(n_points/4)
#     for i in range(n_fourth):
#         a = i / (n_fourth - 1) * 2 - 1 # [-1, 1]
#         t.append( make_point(scale * a, -scale, *color) )
#         r.append( make_point(scale, scale * a, *color) )
#         b.append( make_point(scale * -a, scale, *color) )
#         l.append( make_point(-scale, scale * -a, *color) )
#     return Helios.Frame(*t, *r, *b, *l)
# 
# 
# def pattern_x(scale=1, color=(1,1,1,1), n_points=100):
#     total = 2 + math.sqrt(2) * 2
#     side = int(n_points / total)
#     diag = math.ceil(n_points / total * math.sqrt(2))
# 
#     tl_br = []
#     b = []
#     bl_tr = []
#     t = []
# 
#     for i in range(diag):
#         a = i / (diag-1) * 2 - 1 # [-1, 1]
#         tl_br.append( make_point(scale * a, scale * a, *color) )
#         bl_tr.append( make_point(scale * a, scale * -a, *color) )
# 
#     for i in range(side):
#         a = i / (side-1) * 2 - 1 # [-1, 1]
#         b.append( make_point(scale * -a, scale, 0,0,0,0) )
#         t.append( make_point(scale * -a, -scale, 0,0,0,0) )
# 
#     return Helios.Frame(*tl_br, *b, *bl_tr, *t)
# 
# 
# def pattern_color_hex(scale=1, n_points=100, colors=None):
#     if colors is None:
#         colors = [
#             (1,0,0,1), # red
#             (1,1,0,1), # yellow
#             (0,1,0,1), # green
#             (0,1,1,1), # cyan
#             (0,0,1,1), # blue
#             (1,0,1,1), # magenta
#         ]
#     t = 2 * math.pi / 6
#     sixth = int(n_points / 6)
#     out = []
#     for i in range(6):
#         a = t * i # start angle
#         b = a + t # end angle
#         c = colors[i] # color
#         p1 = (scale * math.cos(a), scale * math.sin(a))
#         p2 = (scale * math.cos(b), scale * math.sin(b))
#         for i in range(sixth):
#             a = i / (sixth-1)
#             p = ( p1[0] + (p2[0]-p1[0])*a, p1[1] + (p2[1]-p1[1])*a )
#             out.append( make_point(p[0], p[1], *c) )
# 
#     return Helios.Frame(*out)

def line(p0, p1, ppl, color=(1,1,1,1)):
    p0x, p0y = p0
    p1x, p1y = p1
    dx = p1x - p0x
    dy = p1y - p0y
    l = math.sqrt( dx*dx + dy*dy )
    n = int(l * ppl)
    out = []
    for i in range(n):
        a = i / (n-1) # [0.0, 1.0]
        x = p0x + a * dx
        y = p0y + a * dy
        out.append( make_point(x, y, *color) )
    return out

def pattern_orientation(scale=1, n_points=100, color_on=(1,1,1,1), color_off=(0,0,0,0)):
    '''an F character
    the top horizontal stroke spans the top of the canvas
    the vertical stroke spans the left of the canvas
    the middle horizontal bar ends at the center of the canvas
    '''
    pattern_len = (5 + math.sqrt(5) + math.sqrt(2)) * scale
    ppl = n_points / pattern_len
    out = []
    s = scale
    out.extend(line( (s, s), (-s, s), ppl, color_on )) # top (left to right)
    out.extend(line( (-s, s), (-s, -s), ppl, color_on )) # left (top to bottom)
    out.extend(line( (-s, -s), (0, 0), ppl, color_off )) # to middle (blank)
    out.extend(line( (0, 0), (-s, 0), ppl, color_on )) # to left middle
    out.extend(line( (-s, 0), (s, s), ppl, color_off )) # to start (blank)
    return out

def pattern_measure(scale=1, n_points=100, color_on=(1,1,1,1), color_off=(0,0,0,0)):
    '''a square with diagonals'''
    # pattern length (square with side 2): 12 + 4 * sqrt(2)
    pattern_len = (12 + 4 * math.sqrt(2)) * scale
    ppl = n_points / pattern_len
    out = []
    s = scale
    out.extend(line( (-s, s), (-s, -s), ppl, color_on )) # top left to bottom left
    out.extend(line( (-s, -s), (s, -s), ppl, color_on )) # bottom left to bottom right
    out.extend(line( (s, -s), (s, s), ppl, color_on )) # bottom right to top right
    out.extend(line( (s, s), (-s, s), ppl, color_on )) # top right to top left
    out.extend(line( (-s, s), (s, -s), ppl, color_on )) # top left to bottom right
    out.extend(line( (s, -s), (s, s), ppl, color_off )) # bottom right to top right (blank)
    out.extend(line( (s, s), (-s, -s), ppl, color_on )) # top right to bottom left
    out.extend(line( (-s, -s), (-s, s), ppl, color_off )) # bottom left to top left (blank)
    return out

def pattern_measure_sq(scale=1, n_points=100, color_on=(1,1,1,1), color_off=(0,0,0,0)):
    pattern_len = 8 * scale
    ppl = n_points / pattern_len
    out = []
    s = scale
    out.extend(line( (-s, s), (-s, -s), ppl, color_on )) # top left to bottom left
    out.extend(line( (-s, -s), (s, -s), ppl, color_on )) # bottom left to bottom right
    out.extend(line( (s, -s), (s, s), ppl, color_on )) # bottom right to top right
    out.extend(line( (s, s), (-s, s), ppl, color_on )) # top right to top left
    return out

def pattern_measure_x(scale=1, n_points=100, color_on=(1,1,1,1), color_off=(0,0,0,0)):
    pattern_len = (4 * math.sqrt(2) + 4) * scale
    ppl = n_points / pattern_len
    out = []
    s = scale
    out.extend(line( (-s, s), (s, -s), ppl, color_on )) # top left to bottom right
    out.extend(line( (s, -s), (s, s), ppl, color_off )) # bottom right to top right (blank)
    out.extend(line( (s, s), (-s, -s), ppl, color_on )) # top right to bottom left
    out.extend(line( (-s, -s), (-s, s), ppl, color_off )) # bottom left to top left (blank)
    return out

def pattern_colors(scale=1, n_points=100):
    '''hexagon with colored sides
    clockwise: red, green, blue, cyan, magenta, yellow
    red starts at the leftmost, vertically centered point, i.e the top half of the hexagon is r,g,b
    '''
    pattern_len = (4/3 * 8) * scale
    ppl = n_points / pattern_len
    out = []
    s = scale
    colors = [
        (1,0,0,1), # R
        (0,1,0,1), # G
        (0,0,1,1), # B
        (0,1,1,1), # C
        (1,0,1,1), # M
        (1,1,0,1), # Y
    ]
    a = -math.pi # start at the left (-180 deg)
    p0 = ( s * math.cos(a), s * math.sin(a) )
    for i in range(6):
        a -= 2 * math.pi / 6
        p1 = ( s * math.cos(a), s * math.sin(a) )
        out.extend(line( p0, p1, ppl, colors[i] ))
        p0 = p1
    return out
    

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
    PPS = 18000
    POINTS = 300
    SCALE = 0.2
    COLOR_SHIFT = 2

    patterns = [
        pattern_orientation(SCALE, POINTS),
        pattern_measure_sq(SCALE, POINTS),
        pattern_measure_x(SCALE, POINTS),
        pattern_measure(SCALE, POINTS),
        pattern_colors(SCALE, POINTS),
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
        Helios.Stop(0)
        Helios.SetShutter(0, 0)
        Helios.CloseDevices()
        exit()
