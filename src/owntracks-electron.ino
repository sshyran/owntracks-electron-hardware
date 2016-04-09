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

int set_interval(String secs);		// Particle function
unsigned int interval = 10;		// "publish" interval in seconds
long last;
double lat;
double lon;
double VCell;
double SoC;

TinyGPSPlus gps;
FuelGauge fuel;

void setup()
{
	RGB.control(true);

	Serial1.begin(9600);

	Time.zone(0);
	lastSync = Time.now();
	lastCell = 0;

	Particle.variable("status", status);
	Particle.function("interval", set_interval);
}

void loop()
{
	unsigned long uptime = millis() / 1000;

	/* sync the clock once a day */
	if (Time.now() > lastSync + 86400) {
		Particle.syncTime();
		lastSync = Time.now();
	}

	/* read battery state every 10 min */
	if (Time.now() > lastCell + 600) {
		VCell = fuel.getVCell();
		SoC = fuel.getSoC();
		lastCell = Time.now();
	}

	/* read gps */
	while (Serial1.available()) {
		char c = Serial1.read();
		gps.encode(c);
	}
	if (gps.location.isValid()) {
		last = Time.now();
		lat = gps.location.lat();
		lon = gps.location.lng();
	}

	/* Status show GPS and Connection status alternating 
	 *
	 * show red LED if gps location is not valid
	 * show greed LED no gps location is available
	 *
	 * show blue LED if connected
	 * show no LED if not connected
	 */
	if (Time.now() % 2 == 0) {
		if (gps.location.isValid()) {
			RGB.color(0, 255, 0);
		} else {
			RGB.color(255, 0, 0);
		}
	} else {
		if (Particle.connected()) {
			RGB.color(0, 0, 255);
		} else {
			RGB.color(0, 0, 0);
		}
	}

	/* set cloud variable */
	snprintf(status, sizeof(status), "%ld,%.6f,%.6f,%.1f,%.1f,%ld",
		last, lat, lon, VCell, SoC, uptime);
}

int set_interval(String secs)
{
	int n = atoi(secs);

	if (n >= 10) {
		interval = n;
	}

	return (1);
}
