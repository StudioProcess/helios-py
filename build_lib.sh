SDK=helios_dac/sdk

# Download helios_dac git submodule, if necessary
if [ ! "$(ls -A helios_dac)" ]; then
  git submodule update --init
fi

mkdir out 2>/dev/null
g++ -Wall -std=c++14 -fPIC -O2 -c -o out/HeliosDacAPI.o $SDK/HeliosDacAPI.cpp
g++ -Wall -std=c++14 -fPIC -O2 -c -o out/HeliosDac.o $SDK/HeliosDac.cpp

mkdir helios/lib 2>/dev/null
if [ $(uname -s) == 'Darwin' ]; then
  g++ -shared -o helios/lib/HeliosDacAPI.dylib out/HeliosDacAPI.o out/HeliosDac.o $SDK/libusb-1.0.0.dylib
  echo "Build platform: $(sw_vers -productName) $(sw_vers -productVersion)\nBuild date: $(date)" > helios/lib/HeliosDacAPI.dylib.buildinfo.txt
fi
if [ $(uname -s) == 'Linux' ]; then
  g++ -shared -o helios/lib/libHeliosDacAPI.so out/HeliosDacAPI.o out/HeliosDac.o $SDK/libusb-1.0.so
  printf "Build platform: $(uname -s) $(uname -r)\nBuild date: $(date)" > helios/lib/libHeliosDacAPI.so.buildinfo.txt
fi
rm -rf out 2>/dev/null
