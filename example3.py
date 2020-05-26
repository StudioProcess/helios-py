import Helios
from helpers import make_point
from helpers import map_coord
import time
import config
import math
import matrix

cfg = config.load('_config.json')

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

# if numDevices is 0:
#     print('Quitting (No Devices found)')
#     exit()

name = Helios.GetName(0)
ver = Helios.GetFirmwareVersion(0)
print(f'Device 0: {name} (FW ver. {ver})')


def test_pattern1(min=0, max=1000):
    '''testpattern of linestrips'''
    a = max-min
    return [
        [ (min, min), (max, min), (max, max), (min, max), (min, min) ], # square
        # [ (min+a/2, min), (max, min+a/2), (min+a/2, max), (min, min+a/2), (min+a/2, min) ], # diamond
        [ (min+a/4, min+a/2), (min+3*a/4, min+a/2) ], # horizontal line
        [ (min+a/2, min+a/4), (min+a/2, min+3*a/4) ]  # vertical line
    ]

def test_pattern2(min=0, max=1000):
    '''testpattern of linestrips'''
    a = max-min
    return [
        [ (min, min), (max, min), ], # top horizontal
        [ (min, max), (max, max) ], # bottom horizontal
    ]

def interpolate_linestrip(ls, step_size = 100):
    '''interpolate list of points'''
    n = len(ls)
    out = []
    for i, p in enumerate(ls[:-1]):
        q = ls[i+1] # next point
        v = ( q[0]-p[0], q[1]-p[1]) # vector from p to q
        d = math.sqrt( v[0] ** 2 + v[1] ** 2 ) # distance between p and q
        steps = math.ceil( d / step_size )
        s = ( v[0]/steps, v[1]/steps )# step vector
        out.append(p) # add first point
        x = p
        for _ in range(steps-1): # don't do the last step
            x = ( x[0]+s[0], x[1]+s[1] )
            out.append(x)
        if i == n-2: out.append(q) # add final point (only on last segment i.e. between indices n-2 and n-1)
    return out

def interpolate_linestrips(lss, fullwidth_steps = 100, min = 0, max = 1000, color = (1,1,1,1), color_off = (0,0,0,0)):
    lss = list( filter(lambda l: len(l) > 0, lss) ) # remove empty linestrips from input
    if len(lss) == 0: return []
    out = []
    step_size = 0xFFF / fullwidth_steps
    for i, l in enumerate(lss):
        # current linestrip
        interp = interpolate_linestrip(l, step_size)
        points = map(lambda p: make_point(p[0], p[1], *color, xmin=min, xmax=max), interp)
        out.extend(points)
        # gap
        next_idx = i+1
        if next_idx == len(lss): next_idx = 0
        m = lss[next_idx] # subsequent linestrip
        gap = interpolate_linestrip([ l[-1], m[0] ], step_size) # linestrip connecting the gap
        # gap = gap[1:-1] # remove first and last point
        points = map(lambda p: make_point(p[0], p[1], *color_off, xmin=min, xmax=max), gap)
        out.extend(points)
    return out


def make_square(size = 2, color = (1, 1, 1, 1)):
    r = size/2
    return [
        make_point(-r, +r, *color),
        make_point(-r, -r, *color),
        make_point(+r, -r, *color),
        make_point(+r, +r, *color),
        # make_point(-r, +r, *color)
    ]

def transform(point_array, transformation_matrix):
    out = []
    for p in point_array:
        p1 = transformation_matrix * [p.x, p.y, 1] # matrix multiplication
        p1 = p1[0] # get column vector
        if p1[2] is not 1: p1[0] /= p1[2]; p1[1] /= p1[2]; p1[2] = 1 # Homogeneous coordinates
        out.append( Helios.Point(int(p1[0]), int(p1[1]), p.r, p.g, p.b, p.i) )
    return out

# barrel/pincushion distortion https://stackoverflow.com/a/6227310
def barrel_distort(point_array, k=0, cx=0, cy=0):
    out = []
    for p in point_array:
        dx = (p.x - cx) / 4095 # distance from center of distortion (but scaled to 0..1)
        dy = (p.y - cy) / 4095
        d = math.sqrt( dx*dx + dy*dy )
        dd = d * (1 + k * d * d) # distorted distance
        if d == 0: d = 1
        nx = cx + dx/d*dd * 4095
        ny = cy + dy/d*dd * 4095
        out.append( Helios.Point(int(nx), int(ny), p.r, p.g, p.b, p.i) )
    return out

def dist(x1, y1, x2, y2):
    return math.sqrt( (x2-x1) ** 2 + (y2-y1) ** 2 )

def interp_attr(attr, obj1, obj2, a):
    return int( getattr(obj1, attr) + (getattr(obj2, attr) - getattr(obj1, attr)) * a )

def interp_attrs(attrs, obj1, obj2, a):
    return [ interp_attr(attr, obj1, obj2, a) for attr in attrs ]
    
def scale_color(color, intensity):
    return [c*intensity for c in color]

# FIXME: this currently duplicates corner points
def interpolate(point_array, fullwidth_steps = 100, close = False):
    step_size = 0xFFF / fullwidth_steps
    # print(step_size)
    out = []
    l = len(point_array)-1
    if close: l += 1
    for i in range(l):
        p0 = point_array[i]
        p1 = point_array[(i+1) % len(point_array)]
        d = dist(p0.x, p0.y, p1.x, p1.y)
        n = int(d / step_size) # number of interpolated points (including start and end)
        if n < 2: n = 2 # include at least start and end
        for j in range(n):
            a = j / (n-1) # interpolation parameter [0, 1]
            attrs = interp_attrs(['x','y','r','g','b','i'] , p0, p1, a)
            out.append( Helios.Point(*attrs) )
            # print(a, attrs)
        # print(i, d, n)
    return out

art = test_pattern2()
art = interpolate_linestrips( art, 10 )
print(art)
# exit()

try:
    info = {'points':0, 'pps':0, 'fps':0}
    while True:
        while Helios.GetStatus(0) is not 1:
            time.sleep(1/1000) # wait 1 ms
        bri = cfg.brightness
        
        # square = make_square(cfg.size, (cfg.r*bri, cfg.g*bri, cfg.b*bri, 1))
        art = test_pattern1()
        art = interpolate_linestrips( art, cfg.interpolation, color=scale_color(cfg.color,bri), color_off=scale_color(cfg.color_off,bri) )
        mat = (
            matrix.translate(cfg.translatex*2047, cfg.translatey*2047) * # 3. apply translation
            matrix.rotate(cfg.rotate, 2047, 2047) * # 2. apply rotatioin
            matrix.scale(cfg.scalex, cfg.scaley, 2047, 2047) # 1. apply scaling
        )
        if cfg.swapxy: mat = matrix.swapxy() * mat # 4.
        if cfg.flipx: mat = matrix.flipx(2047) * mat # 5.
        if cfg.flipy: mat = matrix.flipy(2047) * mat # 6.
        mat = matrix.keystone(cfg.keystonex/4095, cfg.keystoney/4095, 2047, 2047) * mat # 7. apply keystone correction
        art = transform( art, mat )
        
        # square = interpolate(square, cfg.interpolation, close = True)
        art = barrel_distort(art, cfg.barrel, 2047, 2047) # use this on interpolated points, this transform doesn't preserve straight lines
        frame = Helios.Frame(*art)
        # frame = Helios.Frame( make_point(1, 1) )
        if 'fps' in cfg and cfg.fps > 0: pps = len(frame) * cfg.fps
        else: pps = cfg.pps
        pps = min(pps, 24000) # limit this
        new_info = { 'points':len(frame), 'pps':pps, 'fps':int(pps/len(frame)) }
        if new_info != info:
            info = new_info
            print(f'points: {info["points"]}, pps: {info["pps"]}, fps: {info["fps"]}')
        Helios.WriteFrame(0, pps, Helios.FLAGS_DEFAULT, frame, len(frame))
        
        config.update(1)
except KeyboardInterrupt:
    Helios.CloseDevices()
    exit()

Helios.CloseDevices()