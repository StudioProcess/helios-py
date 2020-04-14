import Helios

numDevices = Helios.OpenDevices()
print(f'Found {numDevices} Helios DAC(s)')

if numDevices is 0:
    print('Quitting (No Devices found)')
    exit()

# ret = Helios.SetName(0, 'Helios 825503797')
# print(ret)

name = Helios.GetName(0)
ver = Helios.GetFirmwareVersion(0)
print(f'{name} (FW ver. {ver})')


Helios.CloseDevices()
