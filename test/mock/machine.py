_irq_disable_level = 0


def disable_irq():
    global _irq_disable_level
    _irq_disable_level += 1


def enable_irq(_state):
    global _irq_disable_level
    _irq_disable_level -= 1
    assert _irq_disable_level >= 0


class Pin:
    IRQ_FALLING = 0
    IRQ_LOW_LEVEL = 1
    IRQ_RISING = 2
    IRQ_HIGH_LEVEL = 3

    def __init__(self, num, opt=None):
        self.irqs = [None, None, None, None]

    def irq(self, handler, trigger):
        self.irqs[trigger] = handler

    def poke(self):
        for i in range(4):
            if self.irqs[i] is not None:
                self.irqs[i](self)
