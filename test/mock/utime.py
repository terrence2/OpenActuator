from time import *

_ticks_ms = 0


def ticks_ms():
    global _ticks_ms
    _ticks_ms += 1
    return _ticks_ms
