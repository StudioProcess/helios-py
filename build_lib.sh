SDK=helios_dac/sdk

mkdir out 2>/dev/null
g++ -Wall -std=c++14 -fPIC -O2 -c -o out/HeliosDacAPI.o $SDK/HeliosDacAPI.cpp
g++ -Wall -std=c++14 -fPIC -O2 -c -o out/HeliosDac.o $SDK/HeliosDac.cpp

mkdir lib 2>/dev/null
if [ $(uname -s) == 'Darwin' ]; then
  g++ -shared -o lib/HeliosDacAPI.dylib out/HeliosDacAPI.o out/HeliosDac.o $SDK/libusb-1.0.0.dylib
  echo "Built on: $(sw_vers -productName) $(sw_vers -productVersion)\nBuild date: $(date)" > lib/HeliosDacAPI.readme.txt
fi
if [ $(uname -s) == 'Linux' ]; then
  g++ -shared -o lib/libHeliosDacAPI.so out/HeliosDacAPI.o out/HeliosDac.o $SDK/libusb-1.0.so
  echo "Built on: $(uname -s) $(uname -r)\nBuild date: $(date)" > lib/libHeliosDacAPI.readme.txt
fi
rm -rf out 2>/dev/null
