import os
import sys
sys.path.append(os.path.realpath('./OpenActuator/app_a'))
sys.path.append(os.path.realpath('./test/mock'))

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
    iv.think()
    iv.think()
    iv.think()
    iv.register(machine.Pin.IRQ_FALLING, pin, _lower_half)

    pin.poke()
    iv.think()
    assert called > 0

    iv.think()
    iv.think()
    iv.think()
