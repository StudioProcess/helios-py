#!/usr/bin/env bash

# Access Helios DAC on Linux without root privileges
# See: https://github.com/Grix/helios_dac/blob/master/docs/udev_rules_for_linux.md

rules='ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="1209", ATTRS{idProduct}=="e500", MODE="0660", GROUP="plugdev"'

# add udev rules
sudo echo $rules > /etc/udev/heliosdac.rules
sudo ln -sf /etc/udev/heliosdac.rules /etc/udev/rules.d/011_heliosdac.rules

# add user to plugdev group
sudo useradd -G plugdev $SUDO_USER

# reload udev
sudo udevadm control --reload
