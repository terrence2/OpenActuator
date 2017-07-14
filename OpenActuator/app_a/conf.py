import diagnostic_led
import json


AUTH = None
CONFIG = None
try:
    with open('config/auth.json', 'r') as fp:
        AUTH = json.load(fp)
    with open('config/config.json', 'r') as fp:
        CONFIG = json.load(fp)
except OSError:
    diagnostic_led.blink_forever(100)


def auth():
    return AUTH


def config():
    return CONFIG
