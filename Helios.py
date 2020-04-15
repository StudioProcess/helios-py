'''
BASIC USAGE:
1.  Call OpenDevices() to open devices, returns number of available devices
2.  To send a new frame, first call GetStatus(). If the function returns ready (1) then you can call WriteFrame().
    The status should be polled until it returns ready. It can and sometimes will fail to return ready on the first try.
3.  To stop output, use Stop(). To restart output you must send a new frame as described above.
4.  When the DAC is no longer needed, free it using CloseDevices()

The DAC is double-buffered. When it receives its first frame, it starts outputting it. When a second frame is sent to
the DAC while the first frame is being played, the second frame is stored in the DACs memory until the first frame
finishes playback, at which point the second, buffered frame will start playing. If the DAC finished playback of a frame
without having received and buffered a second frame, it will by default loop the first frame until a new frame is
received (but the flag FLAGS_SINGLE_MODE will make it stop playback instead).
The GetStatus() function actually checks whether or not the buffer on the DAC is empty or full. If it is full, the DAC
cannot receive a new frame until the currently playing frame finishes, freeing up the buffer.
'''

import ctypes
import sys

# Define point structure
class Point(ctypes.Structure):
    _fields_ = [('x', ctypes.c_uint16),
                ('y', ctypes.c_uint16),
                ('r', ctypes.c_uint8),
                ('g', ctypes.c_uint8),
                ('b', ctypes.c_uint8),
                ('i', ctypes.c_uint8)]
    def __repr__(self):
        # return f'Helios.Point(x={self.x}, y={self.y}, r={self.r}, g={self.g}, b={self.b}, i={self.i})'
        return f'Helios.Point({self.x},{self.y}, {self.r},{self.g},{self.b},{self.i})'
    
HeliosPoint = Point # alias

# Helper to create ctypes Arrays of Points
# Call either with a single int to create a Frame with that many Points (initialized to 0)
# or with a variable number of Point instances
def Frame(*args):
    def __repr__(self):
        points = [repr(point) for point in self]
        return f'Helios.Frame({", ".join(points)})'
    
    if type(args[0]) is int:
        FrameType = Point * args[0] # https://docs.python.org/3/library/ctypes.html#arrays
        setattr(FrameType, '__repr__', __repr__)
        return FrameType()
    else:
        FrameType = Point * len(args)
        setattr(FrameType, '__repr__', __repr__)
        return FrameType(*args)

HeliosFrame = Frame # alias

# Flags for WriteFrame() flags argument
FLAGS_DEFAULT           = 0x0
FLAGS_START_IMMEDIATELY = 0x1
FLAGS_SINGLE_MODE       = 0x2
# FLAGS_DONT_BLOCK      = 0x4

# Flags for SetLibusbDebugLogLevel()
LOG_LEVEL_NONE    = 0 # no messages ever printed by the library (default)
LOG_LEVEL_ERROR   = 1 # error messages are printed to stderr
LOG_LEVEL_WARNING = 2 # warning and error messages are printed to stderr
LOG_LEVEL_INFO    = 3 # informational messages are printed to stdout, warning and error messages are printed to stderr
LOG_LEVEL_DEBUG   = 4 # debug and informational messages are printed to stdout, warnings and errors to stderr

# Load and initialize library
_libs = {
    'linux':  './lib/libHeliosDacAPI.so',
    'darwin': './lib/HeliosDacAPI.dylib',
}
if sys.platform in _libs:
    _HeliosLib = ctypes.cdll.LoadLibrary(_libs[sys.platform])
    print(f'Helios Library opened: {_libs[sys.platform]} ({sys.platform})')
else:
    print(f'Platform unsupported: {sys.platform}')

#print(_HeliosLib)
#print( dir(_HeliosLib) )


def OpenDevices():
    '''Initializes drivers, opens connection to all devices
    Returns number of available devices.
    Note: To re-scan for newly connected DACs after this function has once been called before, you must first call CloseDevices().
    '''
    return _HeliosLib.OpenDevices()

def GetStatus(dacNum):
    '''Gets status from the specified DAC
    Returns 1 if ready to receive new frame, 0 if not, -1 if communcation failed
    '''
    return _HeliosLib.GetStatus(dacNum)

def SetLibusbDebugLogLevel(logLevel):
    '''Sets libusb debug log level
    LOG_LEVEL_NONE    (0): no messages ever printed by the library (default)
    LOG_LEVEL_ERROR   (1): error messages are printed to stderr
    LOG_LEVEL_WARNING (2): warning and error messages are printed to stderr
    LOG_LEVEL_INFO    (3): informational messages are printed to stdout, warning and error messages are printed to stderr
    LOG_LEVEL_DEBUG   (4): debug and informational messages are printed to stdout, warnings and errors to stderr
    '''
    return _HeliosLib.SetLibusbDebugLogLevel(logLevel)

def WriteFrame(dacNum, pps, flags, points, numOfPoints):
    '''Writes and outputs a frame to the speficied DAC
    dacNum: DAC number (0 to n where n+1 is the return value from OpenDevices() )
    pps: rate of output in points per second
    flags: (default is 0 or FLAGS_DEFAULT)
        Bit 0 (LSB) = if true, start output immediately, instead of waiting for current frame (if there is one) to finish playing (FLAGS_START_IMMEDIATELY)
        Bit 1 = if true, play frame only once, instead of repeating until another frame is written (FLAGS_SINGLE_MODE)
        Bit 2-7 = reserved
    points: Point data. Either Helios.Frame or list of Helios.Point
    numOfPoints: number of points in the frame to draw
    Returns 1 if successful
    '''
    if type(points) is list: points = Helios.Frame(*points)
    # Note: Using ctypes.byref() instead of ctypes.pointer() cause it's faster apparently. See: https://docs.python.org/3/library/ctypes.html#ctypes.byref
    return _HeliosLib.WriteFrame(dacNum, pps, flags, ctypes.byref(points), numOfPoints)

def SetShutter(dacNum, shutterValue):
    '''Sets the shutter of the specified DAC
    shutterValue 1 = shutter open, shutterValue 0 = shutter closed
    Returns 1 if successful
    '''
    return _HeliosLib.SetShutter(dacNum, shutterValue)

def GetFirmwareVersion(dacNum):
    '''Returns the firmware version numbers
    Returns -1 if communcation failed.
    '''
    return _HeliosLib.GetFirmwareVersion(dacNum)

def GetName(dacNum):
    '''Gets a descriptive name of the specified DAC
    Returns the name if successful
    Returns 0 if the proper name couldn't be fetched from the DAC
    Returns -1 if unsuccessful and name is not populated
    '''
    name = ctypes.create_string_buffer(32) # could also use ctypes.c_char_p() with bytes object
    ret = _HeliosLib.GetName(dacNum, name)
    if ret is 1:
        name = str(name.value, 'ascii')
        return name
    return ret

def SetName(dacNum, name):
    '''Sets a descriptive name for the specified DAC
    name is truncated to 30 characters
    Returns 1 if successful, 0 if the transfer failed
    '''
    name = name[:30] # limit length
    name = ctypes.create_string_buffer( bytes(name, 'ascii') ) # could also use ctypes.c_char_p()
    return _HeliosLib.SetName(dacNum, name)

def Stop(dacNum):
    '''Stops, blanks and centers output on the specified DAC
    Returns 1 if successful
    '''
    return _HeliosLib.Stop(dacNum)

def CloseDevices():
    '''Closes connection to all DACs and frees resources
    Should be called when library is no longer needed (program exit for example)
    '''
    return _HeliosLib.CloseDevices()

def EraseFirmware(dacNum):
    '''Clears the GPNVM1 bit on the DACs microcontroller
    This will cause the DAC to boot into SAM-BA bootloader which allows new firmware to be uploaded over USB.
    '''
    return _HeliosLib.EraseFirmware(dacNum)


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

def make_point(x=0, y=0, r=1, g=1, b=1, i=1):
    return HeliosPoint(
        map_coord(x), map_coord(y),
        *map_color(r, g, b, i)
    )

if __name__ == '__main__':
    if sys.platform not in _libs: exit()
    numDevices = OpenDevices()
    print(f'Helios DACs found: {numDevices}')
    if numDevices is 0: exit()
    for num in range(numDevices):
        name = GetName(num)
        ver = GetFirmwareVersion(num)
        print(f'Device {num}: {name} (FW ver. {ver})')
    CloseDevices()
