from Helios import Point as _Point

def map_coord(x, xmin = -1, xmax = 1):
    return int( (x - xmin) / (xmax - xmin) * 0xFFF )

def map_color_comp(x, xmin = 0, xmax = 1):
    return int( (x - xmin) / (xmax - xmin) * 0xFF )

def map_color(r, g, b, i = 1, min = 0, max = 1):
    return (
        map_color_comp(r, min, max), 
        map_color_comp(g, min, max),
        map_color_comp(b, min, max), 
        map_color_comp(i, min, max)
    )

def make_point(x=0, y=0, r=1, g=1, b=1, i=1, xmin=-1, xmax=1, ymin=None, ymax=None, colormin=0, colormax=1):
    if ymin is None: ymin = xmin
    if ymax is None: ymax = xmax
    return _Point(
        map_coord(x, xmin, xmax), map_coord(y, ymin, ymax),
        *map_color(r, g, b, i, colormin, colormax)
    )