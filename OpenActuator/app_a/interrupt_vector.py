import machine
import utime


class HandlerData:
    def __init__(self, pin, lower_half):
        self.triggered = False
        self.first_trigger_time = 0
        self.last_trigger_time = 0
        self.pin = pin
        self.lower_half = lower_half


class InterruptVector:
    def __init__(self):
        self.triggered = False
        self.handlers = {}

    def register(self, trigger, pin, callback) -> int:
        self.handlers[id(pin)] = HandlerData(pin, callback)
        pin.irq(self._upper_half, trigger)

    def _upper_half(self, pin):
        handler = self.handlers[id(pin)]
        irq_state = machine.disable_irq()
        try:
            self.triggered = True
            if handler.triggered:
                handler.last_trigger_time = utime.ticks_ms()
            else:
                handler.first_trigger_time = utime.ticks_ms()
                handler.triggered = True
        finally:
            machine.enable_irq(irq_state)

    def think(self, ticks_ms):
        irq_state = machine.disable_irq()
        try:
            if not self.triggered:
                return
            self.triggered = False

            for handler in self.handlers.values():
                if handler.triggered:
                    handler.triggered = False
                    handler.lower_half(handler.pin, handler.first_trigger_time, handler.last_trigger_time)
        finally:
            machine.enable_irq(irq_state)
