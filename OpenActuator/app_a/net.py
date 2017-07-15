import diagnostic_led
import conf
import network


def connect_to_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(conf.auth()['wifi']['ssid'], conf.auth()['wifi']['psk'])
        while not sta_if.isconnected():
            diagnostic_led.blink_once(500)
    print('network config: ', sta_if.ifconfig())
