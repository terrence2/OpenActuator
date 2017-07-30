import os
import sys
sys.path.append(os.path.realpath('./OpenActuator/app_a'))
sys.path.append(os.path.realpath('./test/mock'))

if os.path.isfile('LICENSE'):
    os.chdir('./test')
import interrupt_vector

import machine


def test_basic():
    pin = machine.Pin(42)

    called = 0
    def _lower_half(iv_pin, first_call_time, last_call_time):
        nonlocal called
        called += 1
        assert iv_pin == pin

    iv = interrupt_vector.InterruptVector()
    iv.think(10)
    iv.think(20)
    iv.think(30)
    iv.register(machine.Pin.IRQ_FALLING, pin, _lower_half)

    pin.poke()
    iv.think(40)
    assert called > 0

    iv.think(50)
    iv.think(60)
    iv.think(70)
