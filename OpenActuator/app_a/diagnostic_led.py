import machine
import time


DIAGNOSTIC_LED = None
try:
    with open('config/diagnostic_led.pin', 'r') as fp:
        invert = False
        value = int(fp.read())
        if value < 0:
            value = -value
            invert = True
        DIAGNOSTIC_LED = machine.Signal(value, machine.Pin.OUT, invert=invert)
except:
    pass


def blink_forever(cycle_period_ms):
    while True:
        blink_once(cycle_period_ms)


def blink_n(cycle_period_ms, count):
    i = 0
    while i < count:
        blink_once(cycle_period_ms)
        i += 1


def blink_once(cycle_period_ms):
    half_period = cycle_period_ms // 2

    if DIAGNOSTIC_LED is not None:
        DIAGNOSTIC_LED.on()
    time.sleep_ms(half_period)

    if DIAGNOSTIC_LED is not None:
        DIAGNOSTIC_LED.off()
    time.sleep_ms(half_period)

