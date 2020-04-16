import Helios
import time
import config

cfg = config.load('_config.json')

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

if numDevices is 0:
    print('Quitting (No Devices found)')
    exit()

name = Helios.GetName(0)
ver = Helios.GetFirmwareVersion(0)
print(f'Device 0: {name} (FW ver. {ver})')


def make_square(size = 2, color = (1, 1, 1, 1)):
    r = size/2
    return [
        Helios.make_point(-r, +r, *color),
        Helios.make_point(-r, -r, *color),
        Helios.make_point(+r, -r, *color),
        Helios.make_point(+r, +r, *color),
        # Helios.make_point(-r, +r, *color)
    ]

import math
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
    while True:
        while Helios.GetStatus(0) is not 1:
            time.sleep(1/1000) # wait 1 ms
        bri = cfg['brightness']
        square = make_square(cfg['size'], (cfg['r']*bri, cfg['g']*bri, cfg['b']*bri, 1))
        square = interpolate(square, cfg['interpolation'], close = True)
        frame = Helios.Frame(*square)
        # frame = Helios.Frame( Helios.make_point(1, 1) )
        if 'fps' in cfg and cfg['fps'] > 0: pps = len(frame) * cfg['fps']
        else: pps = cfg['pps']
        pps = min(pps, 24000) # limit this
        print(f'points: {len(frame)}, pps: {pps}, fps: {int(pps/len(frame))}')
        Helios.WriteFrame(0, pps, Helios.FLAGS_DEFAULT, frame, len(frame))
        
        config.update(1)
except KeyboardInterrupt:
    Helios.CloseDevices()
    exit()

Helios.CloseDevices()