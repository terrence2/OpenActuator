from machine import Pin
import machine
import utime


class HandlerData:
    def __init__(self, pin, trigger, lower_half):
        self.triggered = False
        self.pin = pin
        self.trigger = trigger
        self.lower_half = lower_half


class InterruptVector:
    def __init__(self):
        self.triggered = False
        self.handlers = {}

    def register(self, trigger, pin, callback):
        self.handlers[(id(pin), trigger)] = HandlerData(pin, trigger, callback)
        pin.irq(self._make_upper_half(trigger), trigger)

    def _make_upper_half(self, trigger):
        def _upper_half(pin):
            irq_state = machine.disable_irq()
            try:
                self.triggered = True
                self.handlers[(id(pin), trigger)].triggered = True
            finally:
                machine.enable_irq(irq_state)
        return _upper_half

    def think(self, ticks_ms):
        irq_state = machine.disable_irq()
        try:
            if not self.triggered:
                return
            self.triggered = False

            for handler in self.handlers.values():
                if handler.triggered:
                    handler.triggered = False
                    handler.lower_half(handler.pin, handler.trigger)
        finally:
            machine.enable_irq(irq_state)
