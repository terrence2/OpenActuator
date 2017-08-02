# OpenActuator
A ~~secure~~ (waiting on ssl server support in the esp8266 micropython implementation),
reliable, and fast ESP userland for lights, motors, buttons, switches, motion detectors,
weather sensors, etc.

## Quick Start Guide
1) Get your hands on an ESP-32 or ESP-8266.
1) Solder whatever fun or interesting hardware you have on hand to it.
1) Describe where you soldered everything in config.json.
1) Flash MicroPython to the device and upload OpenActuator and config.json to the filesystem.
1) Hang it on a wall or something.

## Configuration Guide

OpenActuator is configured with 3 files: diagnostic_led.pin, auth.json, config.json.

### diagnostic_led.pin

Most esp8266 and esp32 boards have an extra LED soldered to one of the pins on
the board. OpenActuator can flash this LED during early boot to display
high-level information about the boot process or problems during boot.
In particular, we want to be able to flash the LED if there are errors
in config.json. Unfortunately, as every board has this LED on a different
pin and some are active high and some active low, we still need to configure
it somehow.

`diagnostic_led.pin` is a flat file in the `config/` directory. Its
content is a single number in textual format (ascii representation)
that designates the pin attached to the LED. If the pin is active low,
negate the number.

Check the `examples` directory for a `diagnostic_led-$MODEL.pin` file
that matches your board model. If there is not one already, please make
one by consulting your board documentation and send a pull request.

### auth.json

At the very least this requires a "wifi" section containing "ssid" and
"psk" for the network you will be connecting to.
```json
{
  "wifi": {
    "ssid": "My Network",
    "psk": "password"
  }
}
```

### config.json

This file has many different sections, each describing a different class of hardware.
The snippets here describe each section independently. They will need to be joined
together into a single json object. If in doubt, see the example configurations in
the example directory.

#### CPU Configuration

The "cpu" object may contain a "freq" key, indicating an overclock. If none
is provided, the default value will be kept.
```json
{
  "cpu": { // optional
    "freq": 160000000, // optional
  },
}
```

#### Main Loop Configuration

In order to support animation, internally, OpenActuator is structured like a
typical game engine. This section allows you to set the desired loop time in
milliseconds via the key "interval". For example, 33ms corresponds to 30
"frames" per second, allowing the loop to animate through 30 values in a second.
A reasonable value here will depend on the CPU's capabilities and the requirements
of the attached hardware.
```json
  "main_loop": {
    "interval": 50,
    "minimum": 10,
  },
```

```json
  "panic_handler": {
    "address": "10.0.0.30",
    "port": 6666,
    "path": "/"
  }

  "http_server": {},
  "http_client": {
    "target": {
      "address": "10.0.0.30",
      "port": 8080
    }
  },

  "buttons": [
    {
      "id": "button-test-1",
      "pin": 12,
      "pull": "up",
      "udp_target": ["10.0.0.30", 33475],
      "http_target": ["10.0.0.30", 9999]
    }
  ],

  "switches": [],

  "motion_detectors": [],

  "leds": [],

  "neopixels": [],
```

#### Weather Station Configuration

OpenActuator supports all of the weather stations that uPython supports directly,
i.e. the DHT11 and DHT22 family (in one-wire mode), as well as some I2C devices,
as yet to be determined. When a measurement is taken every "interval", the values
and the device "id" are sent to the given "udp_target" in json format. The
"id" field can be used to distinguish between multiple sensors reporting to the
same address.
```json
}
  "weather_stations": [
    {
      "type": "DHT22",
      "id": "dht-test-sensor",
      "pin": 14,
      "interval": [5, "m"],
      "udp_target": ["10.0.0.30", 33474]
    }
  ]
}
```

## Detailed Start Guide

### Install the local python environment

First install virtualenv on your system, then:
```
# virtualenv .venv
# . .venv/bin/activate
# pip install --upgrade pip
# pip install -r requirements.txt
```

### Flash micropython to your esp8266

There are ready-to-run images in ./cooked, or download a more recent one. To flash it, follow the instructions in the [intro|http://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html#deploying-the-firmware]. It boils down to something like this:

```
./.venv/bin/esptool.py --port /dev/##something## erase_flash
./.venv/bin/esptool.py --port /dev/##something## --baud 460800 write_flash --flash_size=detect 0 cooked/esp8266-20170612-v1.9.1.bin
```

### Upload OpenActuator to the ESP

When you ran `pip install -r requirements` above, it should have installed ampy. If so, you can do:
```
PORT=/dev/##something## make
```

### Upload your configuration to the ESP

You should have a customized auth.json and config.json in the root directory of the OpenActuator
project. Follow the instructions in the `Configuration Guide` section to craft these files.


