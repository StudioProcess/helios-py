import Helios
import time
import config
import math
import matrix
import re

cfg = config.load('_config.json')

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

if numDevices is 0:
    print('Quitting (No Devices found)')
    exit()

name = Helios.GetName(0)
ver = Helios.GetFirmwareVersion(0)
print(f'Device 0: {name} (FW ver. {ver})')

d = '''
231.56,536.1397646963596
231.56,586.1379980360507
231.56000000000003,636.137858805165
231.56,686.1216426257976
231.56,736.1321803812124
195.4371631027339,750
159.42,736.0122641019523
159.42,686.0148338804705
159.42,636.0036850793562
159.42,586.0126297023788
159.42,536.0076046802685
159.42,486.01161448160894
159.41999999999996,436.0051547337042
159.42,386.0114065902979
159.42,336.0040971298322
159.42,286.0111360221594
159.42,236.01290112949212
190.20637051171977,216.8
240.221385292807,216.8
290.2087298811237,216.8
340.224271021979,216.8
390.1778048664331,217.96517678856847
439.1053824096918,227.75284095406533
483.46104035377505,250.36651163101197
517.8938244026899,286.28962085932494
537.9867091655731,331.80618270397184
543.1555974078178,381.37249551534643
535.4743454521895,430.6162761634588
512.5467719650269,474.75828548431394
475.7399636173248,508.23823155403136
430.02946020364755,528.0275513577461
380.715566522032,535.6617595990001
330.7256682679057,536.13
280.72264141665306,536.13
232.401904296875,479.74
282.39133657414465,479.73999999999995
332.4060777887702,479.74
382.3636388595402,478.75976671695713
429.41201155900956,463.2531858062744
461.18180131673813,425.45576572418213
471.0595893859863,376.8540515136719
460.91458584129805,328.305575633049
429.237822830677,290.39616193294523
382.30639399766915,274.5650645208359
332.3435571304755,273.56
282.3442011475563,273.56
232.35090392977,273.56
231.56,322.7651116832861
231.56,372.7622930196687
231.56,422.7692087544281
231.56,472.7618797667697
'''

d = d.strip().split('\n')
d = list( map(lambda x:x.split(','), d) )
p = []
max = 600
color = (1, 1, 1, 1)
for e in d:
    x = float(e[0])
    y = float(e[1])
    p.append( Helios.make_point(x, y, *color, 0, 600) )

def make_square(size = 2, color = (1, 1, 1, 1)):
    r = size/2
    return [
        Helios.make_point(-r, +r, *color),
        Helios.make_point(-r, -r, *color),
        Helios.make_point(+r, -r, *color),
        Helios.make_point(+r, +r, *color),
        # Helios.make_point(-r, +r, *color)
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
        nx = cx + dx/d*dd * 4095
        ny = cy + dy/d*dd * 4095
        out.append( Helios.Point(int(nx), int(ny), p.r, p.g, p.b, p.i) )
    return out

def dist(x1, y1, x2, y2):
    return math.sqrt( math.pow(x2-x1, 2) + math.pow(y2-y1, 2) )

def interp_attr(attr, obj1, obj2, a):
    return int( getattr(obj1, attr) + (getattr(obj2, attr) - getattr(obj1, attr)) * a )

def interp_attrs(attrs, obj1, obj2, a):
    return [ interp_attr(attr, obj1, obj2, a) for attr in attrs ]

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

try:
    info = {'points':0, 'pps':0, 'fps':0}
    while True:
        while Helios.GetStatus(0) is not 1:
            time.sleep(1/1000) # wait 1 ms
        bri = cfg.brightness
        # square = make_square(cfg.size, (cfg.r*bri, cfg.g*bri, cfg.b*bri, 1))
        square = p
        
        mat = (
            matrix.translate(cfg.translatex*2047, cfg.translatey*2047) * # 3. apply translation
            matrix.rotate(cfg.rotate, 2047, 2047) * # 2. apply rotatioin
            matrix.scale(cfg.scalex, cfg.scaley, 2047, 2047) # 1. apply scaling
        )
        if cfg.swapxy: mat = matrix.swapxy() * mat # 4.
        if cfg.flipx: mat = matrix.flipx(2047) * mat # 5.
        if cfg.flipy: mat = matrix.flipy(2047) * mat # 6.
        mat = matrix.keystone(cfg.keystonex/4095, cfg.keystoney/4095, 2047, 2047) * mat # 7. apply keystone correction
        square = transform( square, mat )
        
        square = interpolate(square, cfg.interpolation, close = True)
        square = barrel_distort(square, cfg.barrel, 2047, 2047) # use this on interpolated points, this transform doesn't preserve straight lines
        frame = Helios.Frame(*square)
        # frame = Helios.Frame( Helios.make_point(1, 1) )
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