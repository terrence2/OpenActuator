from machine import Pin


class Buttons:
    def __init__(self, iv, configs):
        self.buttons = [Button(iv, c) for c in configs]


class Button:
    def __init__(self, iv, config):
        self.pin_number = config['pin']

        pull_config = config['pull'].lower()
        self.pull = -1
        self.active_when = None
        if pull_config == 'up':
            self.pull = Pin.PULL_UP
            self.active_when = 0
        elif pull_config == 'down':
            self.pull = Pin.PULL_DOWN
            self.active_when = 1

        self.active_when = config.get('active_when', self.active_when)
        assert self.active_when is not None, "buttons must specify 'active_when' if no pull is used"

        self.active_edge_trigger = Pin.IRQ_FALLING if self.active_when == 0 else Pin.IRQ_RISING

        self.pin = Pin(self.pin_number, Pin.IN, Pin.PULL_UP)
        iv.register(self.active_edge_trigger, self.pin, self.on_activate_irq)

    def on_activate_irq(self, pin, first_ms, last_ms):
        print("GOT ACTIVATE: {} to {}".format(first_ms, last_ms))



