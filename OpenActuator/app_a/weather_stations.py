import conf
import diagnostic_led
import dht
import json
import machine
import usocket
import utime

MESSAGE = '{{"id":"{}","temperature":{},"humidity":{},"pressure":{}}}'


class WeatherStations:
    def __init__(self, config):
        self.stations = {}
        for station_config in config:
            station = WeatherStation.from_config(station_config)
            self.stations[station.identity] = station

    def think(self, ticks_ms: int):
        for station in self.stations.values():
            station.think(ticks_ms)

    def list(self):
        data = {s.identity: s.show() for s in self.stations.values()}
        content = json.dumps(data)
        return 200, [('Content-Length', str(len(content)))], content

    def show(self, identifier: str):
        content = json.dumps(self.stations[identifier].show())
        return 200, [('Content-Length', str(len(content)))], content


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
        self.target_address = tuple(config['udp_target'])
        self.interval_ms = conf.parse_duration_ms(config.get('interval', [15, 'm']))
        self.last_measure_ms = 0
        self.socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        self.socket.setblocking(False)

    def notify(self, temperature: float, humidity: float, pressure: float):
        data = bytes(MESSAGE.format(self.identity, temperature, humidity, pressure), "ascii")
        self.socket.sendto(data, self.target_address)

    def measure(self):
        raise NotImplementedError("pure virtual")

    def think(self, ticks_ms: int):
        if self.last_measure_ms + self.interval_ms < ticks_ms:
            self.last_measure_ms = ticks_ms
            reading = self.measure()
            if reading is not None:
                self.notify(*reading)

    def show(self):
        return {
            "type": self.__class__.__name__,
            "interval": self.interval_ms / 1000.0,
            "target": list(self.target_address),
        }


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
        self.pin = config['pin']
        self.device = klass(machine.Pin(self.pin))

    def measure(self) -> (float, float, float):
        try:
            t0 = utime.ticks_ms()
            self.device.measure()
            print("WS Measure took: {} ms".format(utime.ticks_ms() - t0))
        except OSError:
            diagnostic_led.blink_n(50, 10)
            return None
        return self.device.temperature(), self.device.humidity(), -1.0

    def show(self):
        data = {
            "pin": self.pin,
            "temperature": self.device.temperature(),
            "humidity": self.device.humidity()
        }
        data.update(super().show())
        return data


class BMWeatherStation(WeatherStation):
    def __init__(self, device_type, config):
        super().__init__()
        klass = {
            "BMP280": None
        }[device_type]

