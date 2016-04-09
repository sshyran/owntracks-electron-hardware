SRC= src/TinyGPS++.cpp src/TinyGPS++.h src/owntracks-electron.ino

owntracks.bin: $(SRC)
	particle compile electron src/ --saveTo owntracks.bin

flash: owntracks.bin
	particle flash --serial owntracks.bin
