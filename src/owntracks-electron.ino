/*
 * owntracks-electron.ino (C)2016 by Christoph Krey
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation, version 2.1 of the License.
 */

#include "TinyGPS++.h"

long lastSync;
long lastCell;

char status[128];

long last;
double lat;
double lon;
double VCell;
double SoC;

TinyGPSPlus gps;
FuelGauge fuel;

unsigned long toggle;

void setup()
{
	RGB.control(true);

	Serial1.begin(9600);

	Time.zone(0);
	lastSync = Time.now();
	lastCell = 0;

	Particle.variable("status", status);
}

void loop()
{
	if (Time.now() > lastSync + 86400) {
		Particle.syncTime();
		lastSync = Time.now();
	}
	for (unsigned long start = millis(); millis() - start < 1000;) {
		while (Serial1.available()) {
			char c = Serial1.read();
			gps.encode(c);
		}
	}

	if (gps.location.isValid()) {
		if (toggle % 2 == 0) {
			RGB.color(0, 255, 0);
		}
		last = Time.now();
		lat = gps.location.lat();
		lon = gps.location.lng();

	} else {
		if (toggle % 2 == 0) {
			RGB.color(255, 0, 0);
		}
	}

	if (toggle % 2 == 1) {
		RGB.color(0, 0, 255);
	}
	if (Time.now() > lastCell + 600) {
		VCell = fuel.getVCell();
		SoC = fuel.getSoC();
		lastCell = Time.now();
	}
	snprintf(status, sizeof(status), "%ld,%.6f,%.6f,%.1f,%.1f",
		last, lat, lon, VCell, SoC);
	toggle++;
	delay(200);
}
