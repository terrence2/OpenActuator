import machine
import utime


class HandlerData:
    def __init__(self, pin, lower_half):
        self.triggered = False
        self.trigger_time = 0
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
        irq_state = machine.disable_irq()
        self.triggered = True
        self.handlers[id(pin)].triggered = True
        self.handlers[id(pin)].trigger_time = utime.ticks_ms()
        machine.enable_irq(irq_state)

    def think(self):
        irq_state = machine.disable_irq()
        if not self.triggered:
            machine.enable_irq(irq_state)
            return
        self.triggered = False

        for handler in self.handlers.values():
            if handler.triggered:
                handler.triggered = False
                handler.lower_half(handler.trigger_time, handler.pin)
        machine.enable_irq(irq_state)
