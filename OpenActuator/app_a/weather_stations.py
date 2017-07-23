import conf
import diagnostic_led
import dht
import machine
import usocket

MESSAGE = '{{"id":"{}","temperature":{},"humidity":{},"pressure":{}}}'


class WeatherStation:
    """
    Base class for all weather station kinds.
    Expected keys are:
        type: str             * Tells us what hardware we are driving.
        interval: [int, str]  * The duration to wait between s
        target: [str, int]    * An IP address/port tuple to send to.
    """
    @staticmethod
    def from_config(config):
        t = config['type']
        if t.startswith('DHT'):
            return DHTWeatherStation(t, config)
        elif t.startswith('BM'):
            return BMWeatherStation(t, config)
        else:
            diagnostic_led.blink_forever(200)

    def __init__(self, config):
        self.identity = config['id']
        self.target_address = tuple(config['target'])
        self.interval_ms = conf.parse_duration_ms(config.get('interval', [300, 's']))
        self.last_measure_ms = 0
        self.socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)

    def notify(self, temperature, humidity, pressure):
        data = bytes(MESSAGE.format(self.identity, temperature, humidity, pressure), "ascii")
        self.socket.sendto(data, self.target_address)

    def think(self, ticks_ms):
        if self.last_measure_ms + self.interval_ms < ticks_ms:
            self.last_measure_ms = ticks_ms
            reading = self.measure()
            if reading is not None:
                self.notify(*reading)


class DHTWeatherStation(WeatherStation):
    """
    Implemenation of the DHT11 and DHT22 "type"s.
    Expected keys are:
        pin: int
    """
    def __init__(self, device_type: str, config):
        super().__init__(config)
        klass = {
            "DHT22": dht.DHT22,
            "DHT11": dht.DHT11
        }[device_type]
        self.device = klass(machine.Pin(config['pin']))

    def measure(self) -> (float, float, float):
        try:
            self.device.measure()
        except OSError:
            diagnostic_led.blink_n(50, 10)
            return None
        return self.device.temperature(), self.device.humidity(), -1.0


class BMWeatherStation(WeatherStation):
    def __init__(self, device_type, config):
        super().__init__()
        klass = {
            "BMP280": None
        }[device_type]

