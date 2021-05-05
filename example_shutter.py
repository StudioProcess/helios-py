import time
from helios import Helios

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

if numDevices is 0:
    print('Quitting (No Devices found)')
    exit()

name = Helios.GetName(0)
ver = Helios.GetFirmwareVersion(0)
print(f'Device 0: {name} (FW ver. {ver})')

try:
    while True:
        shut = Helios.SetShutter(0, 0)
        print('shutter CLOSED:', shut)
        time.sleep(3)
        shut = Helios.SetShutter(0, 1)
        print('shutter OPENED:', shut)
        time.sleep(3)

except KeyboardInterrupt:
    Helios.SetShutter(0, 0)
    Helios.CloseDevices()
    exit()