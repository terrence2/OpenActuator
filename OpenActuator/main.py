import machine
import network
import json
import time

AUTH = None
CONFIG = None


#### FIXME: put this in the config
BUILTIN_LED = machine.Pin(2, machine.Pin.OUT)


def blink_forever(period, duty_cycle=0.5):
    while True:
        blink_once(period, duty_cycle)


def blink_once(period, duty_cycle=0.5):
    BUILTIN_LED.off()
    time.sleep_ms(int(period * duty_cycle))
    BUILTIN_LED.on()
    time.sleep_ms(int(period * (1 - duty_cycle)))


def load_configuration():
    global AUTH
    global CONFIG

    try:
        with open('auth.json', 'r') as fp:
            AUTH = json.load(fp)
        with open('config.json', 'r') as fp:
            CONFIG = json.load(fp)
    except OSError:
        blink_forever(100, 0.25)


def connect_to_network():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(AUTH['wifi']['ssid'], AUTH['wifi']['psk'])
        while not sta_if.isconnected():
            blink_once(500)
    print('network config:', sta_if.ifconfig())


load_configuration()
connect_to_network()
