# electron

** Work in Progres. Maybe. **

This is a proof of concept for implementing an [OwnTracks]-compatible device on a [Particle Electron](https://docs.particle.io/datasheets/electron-datasheet/).

![Electron with GPS](assets/electron.jpg)

The intention was to have the device report via MQTT (which is possible since the [v0.5.0-rc.1 firmware](https://github.com/spark/firmware/releases)), but we've dropped this idea for a number of reasons:

* No TLS
* The TCP traffic churns through the data plan
* possible instability

The second idea, the Electron should periodically and frequently publish a single Particle _variable_ named `status` with a CSV string in, it we also dropped because the CPU load this was causing drained the LiPo in less than 24 hours.

What we now do is the Electron publishes, via the Particle cloud, a variable at a fixed _interval_ (user-configurable by invoking the `interval` Particle function OTA); the device then puts itself into deep sleep mode.

The published _data_ is a CSV string which contains, from left to right:

```
1460104015,48.854458,2.333510,69.0,600
```

* timestamp (`tst`)
* latitude (`lat`)
* longitude (`lon`)
* battery level (`batt`), actually _State of Charge_
* interval (`_interval`)


A backend Python program listens for PRIVATE events named `owntracks` from the the Particle Cloud, verifies the publishing device matches the configured _device_id_, and publishes the data to an MQTT broker in typical [OwnTracks JSON format](http://owntracks.org/booklet/tech/json/), with a `tid` constructed from the last two digits of the Electron's _deviceID_:

```json
{
    "_type": "location",
    "batt": 69.0,
    "lat": 48.854458,
    "lon": 2.33351,
    "tid": "38",
    "_interval": 600,
    "tst": 1460104015
}
```

## Wiring


![Electron with GPS](assets/electron-gps_bb.png)



## Compiling

Compile the `src/` directory in the cloud; if you're on Unix/Linux you should be able to type `make flash`:

```
$ particle compile electron src/ --saveTo owntracks.bin

Compiling code for electron
...

Compile succeeded.
Saved firmware to: owntracks.bin
```

Then flash the resulting firmware file (i.e. `owntracks.bin`) to your Electron using: ([documentation](https://docs.particle.io/guide/tools-and-features/cli/core/#flashing-over-serial-for-the-electron):

```
$ particle flash --serial owntracks.bin
```

## Interval

The Electron will publish at a default interval of 10 seconds. You can change the interval to, say, 600 seconds, with something like:

```bash
#!/bin/sh
access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
devid=nnnnnnnnnnnnnnnnnnnnnnnn

curl https://api.particle.io/v1/devices/${devid}/interval \
	-d access_token="${access_token}" \
	-d arg="600"
```

The new interval is writen to EEPROM and survices loss of power.


## Requirements / Credits

* [TinyGPS++](https://github.com/codegardenllc/tiny_gps_plus), a copy of which is included in `src/`.

  [OwnTracks]: http://owntracks.org
