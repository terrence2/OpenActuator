import os
import sys
sys.path.append(os.path.realpath('./OpenActuator/app_a'))
sys.path.append(os.path.realpath('./test/mock'))

if os.path.isfile('LICENSE'):
    os.chdir('./test')
import interrupt_vector
import buttons
from helpers import threaded

import json
import socket


def test_button_simple():
    # Create the server first so that we always get the message.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(True)
    sock.bind(('127.0.0.1', 12347))

    def _server(_):
        config = {
            "foo": {
                "pin": 42,
                "active": "low",
                "pull": "high",
                "udp_target": ["127.0.0.1", 12347],
                "http_target": ["127.0.0.1", 8080],
            }
        }
        iv = interrupt_vector.InterruptVector()
        btns = buttons.Buttons(iv, config)

        btns.buttons[0].pin.poke()
        iv.think(1)
        btns.think(1)

    with threaded(_server, None):
        raw, _addr = sock.recvfrom(1024)
        data = json.loads(str(raw, 'ascii'))
        assert data['id'] == 'foo'
        assert data['type'] == 'button'
        assert data['seq'] == 0

