from machine import Pin
from micropython import const
import usocket
import utime

MESSAGE = '{{"type":"button","id":"{}","seq":{}}}'
DEFAULT_LOCKOUT = const(10)  # frames


class Buttons:
    def __init__(self, iv, configs):
        self.buttons = [Button(iv, key, config) for key, config in configs.items()]

    def think(self, ticks_ms):
        for btn in self.buttons:
            btn.think(ticks_ms)


class Button:
    def __init__(self, iv, identity, config):
        assert 'pin' in config, "'pin' key is required in button config"
        assert 'active' in config, "'active' key is required in button config"
        assert config['active'] in ('high', 'low'), "button active key must be 'high' or 'low'"
        assert config.get('pull') in ('high', None), "button 'pull' key must be absent or 'high'"
        assert 'udp_target' in config
        assert 'http_target' in config

        self.identity = identity
        self.sequence = 0

        self.pin_number = config['pin']
        pull = {'high': Pin.PULL_UP}.get(config['pull'], -1)
        trigger = {'high': Pin.IRQ_RISING, 'low': Pin.IRQ_FALLING}[config['active']]

        self.udp_target = tuple(config['udp_target'])
        self.udp_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        self.udp_socket.setblocking(False)

        self.http_target = tuple(config['http_target'])

        self.triggered = False
        self.lockout = 0

        self.pin = Pin(self.pin_number, Pin.IN, pull)
        iv.register(trigger, self.pin, self._irq_lower_half)

    def _irq_lower_half(self, _pin, _trigger):
        if self.lockout > 0:
            return
        self.triggered = True
        self.lockout = DEFAULT_LOCKOUT

    def think(self, _ticks_ms):
        if self.lockout > 0:
            self.lockout -= 1

        if self.triggered:
            self.triggered = False
            self.notify()

    def notify(self):
        t0 = utime.ticks_ms()
        msg = bytes(MESSAGE.format(self.identity, self.sequence), 'ascii')
        self.sequence += 1
        self.udp_socket.sendto(msg, self.udp_target)
        print("Button {} sent in {}ms".format(self.identity, utime.ticks_ms() - t0))

