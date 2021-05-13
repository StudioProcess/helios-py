from .Helios import Point as _Point
from .Helios import Frame as _Frame

def map_coord(x, xmin = -1, xmax = 1):
    '''Map coordinate value to 12 bit range [0,0xFFF]'''
    return int( (x - xmin) / (xmax - xmin) * 0xFFF )

def map_color_comp(x, xmin = 0, xmax = 1):
    '''Map color component value to 8 bit range [0,0xFF]'''
    return int( (x - xmin) / (xmax - xmin) * 0xFF )

def map_color(r, g, b, i = 1, min = 0, max = 1):
    '''Map 4-channel (r/g/b/intensity) color value to 8 bit per component'''
    return (
        map_color_comp(r, min, max), 
        map_color_comp(g, min, max),
        map_color_comp(b, min, max), 
        map_color_comp(i, min, max)
    )

def clip_coord(x):
    '''Clip coordinate value to [0,0xFFF]'''
    return min(0xFFF, max(0, x))

def make_point(x=0, y=0, r=1, g=1, b=1, i=1, xmin=-1, xmax=1, ymin=None, ymax=None, colormin=0, colormax=1, clip=True):
    '''Create Helios.Point instance while mapping value ranges'''
    if ymin is None: ymin = xmin
    if ymax is None: ymax = xmax
    x = map_coord(x, xmin, xmax)
    y = map_coord(y, ymin, ymax)
    if clip:
        x = clip_coord(x)
        y = clip_coord(y)
    c = map_color(r, g, b, i, colormin, colormax)
    return _Point(x, y, *c)

def color_shift_frame(frame, shift_val):
    '''Shift color values in frame (relative to positions) to compensate for scanner movement lag'''
    shift_val = round(shift_val)
    n = len(frame)
    out = _Frame(n)
    for i, p in enumerate(frame):
        out[i].x = p.x
        out[i].y = p.y
        j = i - shift_val # shifted index (for color components)
        while j < 0: j += n
        j %= n
        q = frame[j]
        out[i].r = q.r
        out[i].g = q.g
        out[i].b = q.b
        out[i].i = q.i
    return out
